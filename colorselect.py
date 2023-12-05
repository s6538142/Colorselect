import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageGrab  # 添加ImageGrab模組
import pyautogui




def find_color(image, target_color, tolerance):
    global img_ref
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
    global img_ref
    file_path = filedialog.askopenfilename()
    if file_path:
        img = Image.open(file_path)    
        img_ref = img  # 更新 img_ref 變數為打開的圖像

        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

        # 貼上圖片後立即觸發顏色搜尋
        find_target_color()

def paste_image():
    global img_ref, cropped_image
    img = ImageGrab.grabclipboard()  # 從剪貼上取得圖片
    if img:
        img_ref = img  # 將 img_ref 設置為新貼上的圖像
        cropped_image = img  # 或將 cropped_image 設置為新貼上的圖像

        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

        # 貼上圖片後立即觸發顏色搜尋
        find_target_color()
        
def create_button_callback(x, y):
    def inner_callback():
        print(f"Button clicked at coordinates: ({x}, {y})")
        try:
            # 取得移動前的鼠標位置
            prev_mouse_x, prev_mouse_y = pyautogui.position()

            # 取得 image_label 相對於畫面左上角的位置
            image_x, image_y = image_label.winfo_rootx(), image_label.winfo_rooty()

            # 將滑鼠移動到 image_label 左上角座標
            pyautogui.moveTo(image_x, image_y, duration=0.25)

            # 相對於 image_label 左上角座標進行移動
            pyautogui.move(x, y, duration=0.25)

            # 取得移動後的鼠標位置
            new_mouse_x, new_mouse_y = pyautogui.position()

            # 切回主視窗
            root.deiconify()

            # 如果鼠標位置沒有改變，可能移動失敗
            if (prev_mouse_x, prev_mouse_y) == (new_mouse_x, new_mouse_y):
                print("Mouse movement failed.")

            # 否則顯示 image_label 中對應座標的像素顏色
            else:
                label_x, label_y = x - image_label.winfo_rootx(), y - image_label.winfo_rooty()
                label_pixel_rgb = img_ref.getpixel((label_x, label_y))[:3]
                print(f"Color at image_label coordinates ({label_x}, {label_y}): RGB {label_pixel_rgb}")

        except Exception as e:
            print(f"Error: {e}")

    return inner_callback


def get_pixel_color(event):
    x, y = event.x, event.y
    
    # 確認有圖片可供使用
    if img_ref or cropped_image:
        # 檢查使用的圖片
        if img_ref:
            image = img_ref
        else:
            image = cropped_image

        # 取得滑鼠點擊位置的像素顏色
        label_pixel_rgb = image.getpixel((x, y))[:3]
        
        # 顯示滑鼠點擊的座標和像素顏色
        print(f"Color at clicked coordinates ({x}, {y}): RGB {label_pixel_rgb}")
        
        # 更新滑鼠座標在coordinates_label中
        coordinates_label.config(text=f"滑鼠座標: (x={x}, y={y})")
        
        # 將獲得的像素顏色顯示在 rgb_label 中
        rgb_label.config(text=f"RGB: {label_pixel_rgb}")
        
        # 顯示點擊位置的像素顏色在color_preview_label中
        color_preview = Image.new('RGB', (50, 50), color=label_pixel_rgb)
        color_preview = ImageTk.PhotoImage(color_preview)
        color_preview_label.config(image=color_preview)
        color_preview_label.image = color_preview




# 更新 create_scrollable_result_window 函數，將按鈕的 command 設置為 create_button_callback(x, y)
def create_scrollable_result_window(matches):
    result_window = tk.Toplevel(root)
    result_window.title("搜尋結果")
    
    row_count = len(matches)
    column_count = 4  # 4列

    for i in range(row_count):
        for j in range(column_count):
            if j < len(matches[i]):
                x, y = matches[i][j]
                pixel_rgb = img_ref.getpixel((x, y))[:3]

                frame = tk.Frame(result_window, relief=tk.RIDGE, borderwidth=2)
                frame.grid(row=i, column=j, padx=5, pady=5)

                color_preview = Image.new('RGB', (20, 20), color=pixel_rgb)
                color_preview = ImageTk.PhotoImage(color_preview)
                color_preview_label = tk.Label(frame, image=color_preview)
                color_preview_label.image = color_preview
                color_preview_label.pack(side=tk.LEFT)

                # 將 command 設置為 create_button_callback(x, y)
                btn = tk.Button(frame, text=f"({x},{y}) RGB: {pixel_rgb}", command=create_button_callback(x, y))
                btn.pack(side=tk.LEFT)



def find_target_color():
    global img_ref, cropped_image

    target_color = (int(target_r_entry.get()), int(target_g_entry.get()), int(target_b_entry.get()))
    tolerance = (int(tolerance_r_entry.get()), int(tolerance_g_entry.get()), int(tolerance_b_entry.get()))

    if cropped_image:
        img_ref = cropped_image
        cropped_image = img_ref.copy()
    else:
        img_ref = img_ref

    matches = find_color(img_ref, target_color, tolerance)

    formatted_matches = [matches[i:i + 4] for i in range(0, len(matches), 4)]
    create_scrollable_result_window(formatted_matches)






def show_coordinates(event):
    x, y = event.x, event.y
    global img_ref
    if img_ref and not isinstance(root.focus_get(), tk.Toplevel):
        image = img_ref  # 使用 img_ref 作為圖像
    elif cropped_image:
        image = cropped_image
    else:
        return

    coordinates_label.config(text=f"滑鼠座標: (x={x}, y={y})")

    pixel_rgb = image.getpixel((x, y))[:3]
    rgb_label.config(text=f"RGB: {pixel_rgb}")

    color_preview = Image.new('RGB', (50, 50), color=pixel_rgb)
    color_preview = ImageTk.PhotoImage(color_preview)
    color_preview_label.config(image=color_preview)
    color_preview_label.image = color_preview

# 在程式的開頭設定一個暫存區
cropped_image = None

def take_screenshot():
    global img_ref, cropped_image
    img_ref = None
    cropped_image = None
    image_label.config(image='')

    root.withdraw()
    root.after(500, grab_screen)

def grab_screen():
    global cropped_image
    img = ImageGrab.grab()
    root.deiconify()

    if img:
        cropped_image = img  # 將裁剪後的圖像設置為 cropped_image

        root.iconify()

        # 更新 image_label

        screenshot_window = tk.Toplevel(root)
        screenshot_window.title("截圖")
        screenshot_window.overrideredirect(True)

        canvas = tk.Canvas(screenshot_window, width=img.width, height=img.height, bg="white", highlightthickness=0)
        canvas.pack()

        photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo

        start_x, start_y = None, None

        def on_click(event):
            nonlocal start_x, start_y
            start_x, start_y = event.x, event.y

        def on_drag(event):
            nonlocal start_x, start_y
            end_x, end_y = event.x, event.y

            canvas.delete("rect")
            canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", tags="rect")

        def on_release(event):
            nonlocal start_x, start_y
            end_x, end_y = event.x, event.y

            canvas.delete("rect")
            cropped_img = img.crop((start_x, start_y, end_x, end_y))

            # 存储裁剪后的图像到 cropped_image 变量
            global cropped_image
            cropped_image = cropped_img

            # 销毁截图窗口，显示主窗口
            screenshot_window.destroy()
            root.deiconify()

            # 更新 image_label
            update_image_label()

        # 添加更新 image_label 的函数
        def update_image_label():
            global cropped_image
            if cropped_image:
                # 清空图像标签
                image_label.config(image='')

                # 将裁剪后的图像显示在 image_label
                cropped_photo = ImageTk.PhotoImage(cropped_image)
                image_label.config(image=cropped_photo)
                image_label.image = cropped_photo

    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<ButtonRelease-1>", on_release)
        
# 添加清空 image_label 的函數
def clear_image_label():
    image_label.config(image='')



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

click_label = tk.Label(root, text="請在圖片上重新點擊以取得座標")
click_label.pack()


# 按鈕並排
button_frame = tk.Frame(root)
button_frame.pack()

find_button = tk.Button(button_frame, text="尋找顏色", command=find_target_color)
find_button.pack(side=tk.LEFT, padx=5)

open_button = tk.Button(button_frame, text="打開圖片", command=open_image)
open_button.pack(side=tk.LEFT, padx=5)

paste_button = tk.Button(button_frame, text="貼上圖片", command=paste_image)

screenshot_button = tk.Button(button_frame, text="截圖", command=take_screenshot)
screenshot_button.pack(side=tk.LEFT, padx=5)
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
image_label.bind("<Button-1>", get_pixel_color)

root.mainloop()
