import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageGrab  # 添加ImageGrab模块


def find_color(image, target_color, tolerance):
    width, height = image.size
    matches = []  # 存儲符合條件的像素位置

    # 遍歷圖像每個像素
    for y in range(height):
        for x in range(width):
            pixel_color = image.getpixel((x, y))[:3]  # 取得該像素的RGB值

            # 檢查該像素是否在目標顏色的色差範圍內
            in_tolerance = all(abs(pixel_color[i] - target_color[i]) <= tolerance[i] for i in range(3))
            
            if in_tolerance:
                matches.append((x, y))  # 將符合條件的像素位置添加到列表中

    return matches  # 返回所有符合條件的像素位置列表

def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global img_ref
        img = Image.open(file_path)
        img.thumbnail((300, 300))
        img_ref = img

        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

def paste_image():
    img = ImageGrab.grabclipboard()  # 從剪貼上取得圖片
    if img:
        global img_ref
        img_ref = img

        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

def find_target_color():
    # 取得使用者輸入的顏色值和色差範圍
    target_r = int(target_r_entry.get())
    target_g = int(target_g_entry.get())
    target_b = int(target_b_entry.get())
    target_color = (target_r, target_g, target_b)
    
    tolerance_r = int(tolerance_r_entry.get())
    tolerance_g = int(tolerance_g_entry.get())
    tolerance_b = int(tolerance_b_entry.get())
    tolerance = (tolerance_r, tolerance_g, tolerance_b)
    
    matches = find_color(img_ref, target_color, tolerance)

    # 格式化輸出符合條件的像素位置
    formatted_matches = [matches[i:i + 10] for i in range(0, len(matches), 10)]
    formatted_text = "\n".join(f"{i+1}-{i+len(sublist)}: {sublist}" for i, sublist in enumerate(formatted_matches))
    
    # 將所有符合條件的像素位置列印出來
    result_label.config(text=f"Found {len(matches)} matching pixels:\n{formatted_text}")

def show_coordinates(event):
    x, y = event.x, event.y
    if img_ref:
        coordinates_label.config(text=f"滑鼠座標: (x={x}, y={y})")

        pixel_rgb = img_ref.getpixel((x, y))[:3]
        rgb_label.config(text=f"RGB: {pixel_rgb}")

        color_preview = Image.new('RGB', (50, 50), color=pixel_rgb)
        color_preview = ImageTk.PhotoImage(color_preview)
        color_preview_label.config(image=color_preview)
        color_preview_label.image = color_preview



root = tk.Tk()
root.title("尋找圖片中的顏色")
root.geometry("400x450")

img_ref = None


# 使用 Frame 包裝橫向排列的輸入框
target_color_frame = tk.Frame(root)
target_color_frame.pack()

entry_width = 5  # 輸入框寬度

target_color_label = tk.Label(target_color_frame, text="輸入尋找的顏色 (R,G,B):")
target_color_label.pack(side=tk.LEFT)

target_r_entry = tk.Entry(target_color_frame)
target_r_entry.pack(side=tk.LEFT, padx=5)
target_r_entry.config(width=entry_width)

target_g_entry = tk.Entry(target_color_frame)
target_g_entry.pack(side=tk.LEFT, padx=5)
target_g_entry.config(width=entry_width)

target_b_entry = tk.Entry(target_color_frame)
target_b_entry.pack(side=tk.LEFT, padx=5)
target_b_entry.config(width=entry_width)



# 使用 Frame 包裝橫向排列的輸入框（色差值）
tolerance_frame = tk.Frame(root)
tolerance_frame.pack()

tolerance_label = tk.Label(tolerance_frame, text="輸入RGB色差值 (R,G,B):")
tolerance_label.pack(side=tk.LEFT)

tolerance_r_entry = tk.Entry(tolerance_frame)
tolerance_r_entry.pack(side=tk.LEFT, padx=5)
tolerance_r_entry.config(width=entry_width)

tolerance_g_entry = tk.Entry(tolerance_frame)
tolerance_g_entry.pack(side=tk.LEFT, padx=5)
tolerance_g_entry.config(width=entry_width)

tolerance_b_entry = tk.Entry(tolerance_frame)
tolerance_b_entry.pack(side=tk.LEFT, padx=5)
tolerance_b_entry.config(width=entry_width)


# 兩個按鈕並排
button_frame = tk.Frame(root)
button_frame.pack()

find_button = tk.Button(button_frame, text="尋找顏色", command=find_target_color)
find_button.pack(side=tk.LEFT, padx=5)

open_button = tk.Button(button_frame, text="打開圖片", command=open_image)
open_button.pack(side=tk.LEFT, padx=5)

paste_button = tk.Button(button_frame, text="貼上圖片", command=paste_image)
paste_button.pack(side=tk.LEFT, padx=5)
# 中間部分

coordinates_label = tk.Label(root, text="")
coordinates_label.pack()

rgb_label = tk.Label(root, text="")
rgb_label.pack()

color_preview_label = tk.Label(root)
color_preview_label.pack()

# 下方部分

image_label = tk.Label(root)
image_label.pack()

result_label = tk.Label(root, text="")
result_label.pack()




# Bind mouse motion to the image_label
image_label.bind("<Motion>", show_coordinates)

root.mainloop()

