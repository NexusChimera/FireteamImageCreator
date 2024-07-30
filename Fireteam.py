import os
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont
import pyautogui
import time
import ctypes
import win32api
import win32con

def load_config():
    config = {}
    with open('config.txt', 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=')
                config[key] = value
    return config

async def fetch(session, url, headers=None, method='GET', json=None, params=None):
    async with session.request(method, url, headers=headers, json=json, params=params) as response:
        return await response.json() if response.status == 200 else None

async def download_asset(session, url, filename):
    async with session.get(url) as response:
        if response.status == 200:
            with open(filename, 'wb') as file:
                file.write(await response.read())

async def search_player(session, bungie_name, bungie_code, headers):
    search_url = f"https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayerByBungieName/-1/"
    payload = {"displayName": bungie_name, "displayNameCode": bungie_code}
    return await fetch(session, search_url, headers=headers, method='POST', json=payload)

async def get_profile_data(session, membership_type, destiny_membership_id, headers):
    url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{destiny_membership_id}/"
    params = {'components': '200,201,205,1000'}
    return await fetch(session, url, headers=headers, params=params)

async def get_item_definition(session, item_hash, headers):
    url = f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/{item_hash}/"
    return await fetch(session, url, headers=headers)

async def get_user_info(session, membership_id, headers):
    url = f"https://www.bungie.net/Platform/User/GetMembershipsById/{membership_id}/254/"
    return await fetch(session, url, headers=headers)

async def organize_assets(session, guardian_data, font_path, font_size, text_color, headers):
    tasks = []
    guardian_data.sort(key=lambda x: x['bungie_name'].lower())
    for idx, member_data in enumerate(guardian_data, start=1):
        folder = f"guardian{idx}"
        os.makedirs(folder, exist_ok=True)
        emblem_url = f"https://www.bungie.net{member_data['character_data']['emblemBackgroundPath']}"
        emblem_filename = f"{folder}/image2.jpg"
        tasks.append(download_asset(session, emblem_url, emblem_filename))

    await asyncio.gather(*tasks)

    for idx, member_data in enumerate(guardian_data, start=1):
        folder = f"guardian{idx}"
        emblem_filename = f"{folder}/image2.jpg"
        resize_image(emblem_filename, 474, 96)
        add_text_to_image(emblem_filename, member_data['bungie_name'], font_path, font_size, text_color)

    ghost_tasks = []
    for idx, member_data in enumerate(guardian_data, start=1):
        folder = f"guardian{idx}"
        ghost_item = member_data['ghost_item']
        if ghost_item:
            ghost_tasks.append(fetch_ghost(session, ghost_item['itemHash'], folder, headers))

    await asyncio.gather(*ghost_tasks)

async def fetch_ghost(session, item_hash, folder, headers):
    item_definition = await get_item_definition(session, item_hash, headers)
    if item_definition and 'Response' in item_definition and 'displayProperties' in item_definition['Response']:
        ghost_url = f"https://www.bungie.net{item_definition['Response']['displayProperties']['icon']}"
        ghost_filename = f"{folder}/image3.jpg"
        await download_asset(session, ghost_url, ghost_filename)
        resize_image(ghost_filename, 175, 175)

def resize_image(image_path, width, height):
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img.resize((width, height)).save(image_path)

def add_text_to_image(image_path, text, font_path, initial_font_size, text_color):
    with Image.open(image_path) as image:
        image = image.convert('RGB')
        draw = ImageDraw.Draw(image)
        font_size = initial_font_size
        font = ImageFont.truetype(font_path, font_size)
        indent = 120
        max_width = image.width - indent
        while True:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= max_width or font_size <= 10:
                break
            font_size -= 1
            font = ImageFont.truetype(font_path, font_size)
        text_height = text_bbox[3] - text_bbox[1]
        x = indent
        y = (image.height - text_height) / 2 - 10
        outline_color = 'black'
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=text_color)
        image.save(image_path)

async def main():
    print("Running...\nSwitch back to Destiny 2 and open the Nearby list")
    config = load_config()
    bungie_name, bungie_code = config['bungie_name'].split('#')
    api_key = config['bungie_api_key']
    headers = {'X-API-Key': api_key}
    font_path = "Lato-Bold.ttf"
    font_size = 40
    text_color = "rgb(255,255,255)"
    async with aiohttp.ClientSession() as session:
        guardian_data = await search_player(session, bungie_name, bungie_code, headers)
        if not guardian_data or 'Response' not in guardian_data or not guardian_data['Response']:
            print("No guardian data found.")
            return
        guardian = guardian_data['Response'][0]
        membership_id = guardian['membershipId']
        membership_type = guardian['membershipType']
        profile_data = await get_profile_data(session, membership_type, membership_id, headers)
        if not profile_data or 'Response' not in profile_data:
            print("No profile data found.")
            return
        fireteam_members = profile_data['Response']['profileTransitoryData']['data']['partyMembers']
        if not fireteam_members:
            print("No fireteam members found.")
            return
        members_data = []
        user_tasks = []
        for member in fireteam_members:
            user_tasks.append(fetch_member_data(session, member, headers, members_data))
        await asyncio.gather(*user_tasks)
        await organize_assets(session, members_data, font_path, font_size, text_color, headers)
        guardian_position = next((idx + 1 for idx, member in enumerate(members_data) if member['bungie_name'].lower() == bungie_name.lower()), None)
        if guardian_position is None:
            print("Guardian position not found.")
            return
        num_members = len(members_data)
        y_ratios = [0.247 + i * 0.054 for i in range(num_members)]
        for pos, y_ratio in enumerate(y_ratios, start=1):
            perform_steps(pos, 0.236, y_ratio, special=(pos == guardian_position))
        folders = [f"guardian{i}" for i in range(1, num_members + 1)]
        for folder in folders:
            overlay_images(folder)
        combine_images(folders, "combined_image.png")
        combined_image_folder = os.path.dirname(os.path.abspath("combined_image.png"))
        os.startfile(combined_image_folder)

async def fetch_member_data(session, member, headers, members_data):
    member_info = await get_user_info(session, member['membershipId'], headers)
    if not member_info or 'Response' not in member_info:
        return
    member_display_name = next((m['bungieGlobalDisplayName'] for m in member_info['Response']['destinyMemberships'] if m['membershipId'] == member['membershipId']), None)
    member_membership_type = next((m['membershipType'] for m in member_info['Response']['destinyMemberships'] if m['membershipId'] == member['membershipId']), None)
    if not member_display_name or not member_membership_type:
        return
    member_profile_data = await get_profile_data(session, member_membership_type, member['membershipId'], headers)
    if not member_profile_data or 'Response' not in member_profile_data:
        return
    character_data = member_profile_data['Response']['characters']['data']
    equipment_data = member_profile_data['Response']['characterEquipment']['data']
    most_recent_character = max(character_data.items(), key=lambda x: x[1]['dateLastPlayed'])[0]
    ghost_item = next((item for item in equipment_data[most_recent_character]['items'] if item['bucketHash'] == 4023194814), None)
    members_data.append({
        'bungie_name': member_display_name,
        'character_data': character_data[most_recent_character],
        'ghost_item': ghost_item
    })

def block_mouse_input(block=True):
    ctypes.windll.user32.BlockInput(True if block else False)

def press_key(key):
    vk_code = ord(key.upper())
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)

def press_special_key(key, double_press=False):
    special_keys = {']': 0xDD, 'esc': win32con.VK_ESCAPE}
    vk_code = special_keys.get(key)
    if vk_code:
        for _ in range(2 if double_press else 1):
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)

def perform_steps(position, x_ratio, y_ratio, special=False):
    screen_width, screen_height = pyautogui.size()
    x = int(screen_width * x_ratio)
    y = int(screen_height * y_ratio)
    right_click_x = int(screen_width * 0.725)
    right_click_y = int(screen_height * 0.369)
    block_mouse_input(True)
    try:
        if not special:
            pyautogui.moveTo(x, y)
            time.sleep(0.5)
            pyautogui.click(button='right')
            time.sleep(0.5)
            press_key('s')
            time.sleep(0.5)
            pyautogui.moveTo(right_click_x, right_click_y)
            time.sleep(0.5)
            pyautogui.click(button='right')
            time.sleep(0.5)
            pyautogui.moveTo(100, 100)
            time.sleep(1.5)
            pyautogui.screenshot(f'guardian{position}/image1.png')
            crop_and_resize_image(f'guardian{position}/image1.png', 474)
            press_special_key(']', double_press=True)
        else:
            press_key('i')
            time.sleep(0.5)
            press_key('s')
            time.sleep(0.5)
            pyautogui.moveTo(right_click_x, right_click_y)
            time.sleep(0.5)
            pyautogui.click(button='right')
            time.sleep(0.5)
            pyautogui.moveTo(100, 100)
            time.sleep(1.5)
            pyautogui.screenshot(f'guardian{position}/image1.png')
            crop_and_resize_image(f'guardian{position}/image1.png', 474)
            press_special_key(']', double_press=False)
    finally:
        block_mouse_input(False)
        time.sleep(0.5)

def crop_and_resize_image(image_path, new_width):
    screen_width, screen_height = pyautogui.size()
    with Image.open(image_path) as img:
        crop_box = (int(2270 / 3840 * screen_width), 0, int(3250 / 3840 * screen_width), screen_height)
        cropped_img = img.crop(crop_box)
        resized_img = cropped_img.resize((new_width, int(screen_height * (new_width / (crop_box[2] - crop_box[0])))))
        resized_img.save(image_path)

def combine_images(folder_paths, output_path):
    images = [Image.open(os.path.join(folder, "output.png")) for folder in folder_paths]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    combined_image = Image.new('RGB', (total_width, max_height), 'black')
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width
    combined_image.save(output_path)
    for img in images:
        img.close()
    for folder in folder_paths:
        for file_name in os.listdir(folder):
            os.remove(os.path.join(folder, file_name))
        os.rmdir(folder)

def overlay_images(folder_path):
    image_paths = [f"{folder_path}/image1.png", f"{folder_path}/image2.jpg", f"{folder_path}/image3.jpg"]
    images = [Image.open(path) for path in image_paths if os.path.exists(path)]
    if len(images) == 3:
        combined_image = Image.new('RGB', images[0].size)
        combined_image.paste(images[0], (0, 0))
        combined_image.paste(images[2], ((images[0].width - images[2].width) // 2, images[0].height - images[2].height - images[1].height))
        combined_image.paste(images[1], (0, images[0].height - images[1].height))
        combined_image.save(f"{folder_path}/output.png")
        for img in images:
            img.close()
        for path in image_paths:
            os.remove(path)

if __name__ == "__main__":
    asyncio.run(main())
