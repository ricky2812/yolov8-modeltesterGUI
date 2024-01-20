from pickle import GLOBAL
import cv2, psutil, sys, win32api, win32event
import tkinter as tk
from PIL import Image, ImageTk
Image.CUBIC = Image.BICUBIC # CUBIC is deprecated but tkinter uses it by default
import ttkbootstrap as ttk
from tkinter import filedialog
from ultralytics import YOLO
from winerror import ERROR_ALREADY_EXISTS


#YOLOv8 Model Viewer Demo

mutex = win32event.CreateMutex(None, False, 'name')
last_error = win32api.GetLastError()
if last_error == ERROR_ALREADY_EXISTS:
   sys.exit(0)

import os
path = os.path.dirname(__file__)
weight = os.path.join(path,'detection.pt')
light = os.path.join(path,'yolov8.jpeg')
dark = os.path.join(path,'yolov8.jpeg')
icon = os.path.join(path, 'icon.ico')
# Global variables for OpenCV-related objects and flags
cap = None
is_camera_on = False
frame_count = 0
frame_skip_threshold = 3
model = YOLO(weight)
video_paused = False
text_output = {}



def change_lighing():
    if colorstyle.get() == 'light':
        initial_image = Image.open(light)
        style.theme_use("sandstone")
    else:
        initial_image = Image.open(dark)
        style.theme_use("darkly")
    if is_camera_on == False:
        resized_image = initial_image.resize((640, 480))
        processed_photo = ImageTk.PhotoImage(image=resized_image)
        canvas.img = processed_photo
        canvas.create_image(0, 0, anchor=tk.NW, image=processed_photo)

# Function to start the webcam feed
def start_webcam():
    global cap, is_camera_on, video_paused
    if not is_camera_on:
        cap = cv2.VideoCapture(0)  # Use the default webcam (you can change the index if needed)
        is_camera_on = True
        video_paused = False
        update_canvas()  # Start updating the canvas

# Function to stop the webcam feed
def stop_webcam():
    global cap, is_camera_on, video_paused
    if cap is not None:
        cap.release()
        is_camera_on = False
        video_paused = False
    change_lighing()
    console.delete(1.0, tk.END)

# Function to pause or resume the video
def pause_resume_video():
    global video_paused
    video_paused = not video_paused

# Function to start video playback from a file
def select_file():
    global cap, is_camera_on, video_paused
    if is_camera_on:
        stop_webcam()  # Stop the webcam feed if running
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if file_path:
        cap = cv2.VideoCapture(file_path)
        is_camera_on = True
        video_paused = False
        update_canvas()  # Start updating the canvas with the video

# Function to update the Canvas with the webcam frame or video frame
def update_canvas():
    global is_camera_on, frame_count, video_paused
    if is_camera_on:
        if not video_paused:
            ret, frame = cap.read()
            if ret:
                max_fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count += 1
                if frame_count % frame_skip_threshold != 0:
                    canvas.after(10, update_canvas)
                    return

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (1020, 500))

                results = model.predict(frame,verbose=False)         
                detections = results[0]
        
                
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                
                speed = detections.speed
                speed = speed['preprocess'] + speed['inference'] + speed['postprocess']
                if speed != 0:
                    fps = int(1000/speed)
                    if max_fps > fps:
                        fps = int(1000 / speed)
                        # fps_gauge.configure(value=int(1000 / speed))
                    else:
                        fps = max_fps
                        # fps_gauge.configure(value=max_fps)
                else:
                    fps = max_fps
                    # fps_gauge.configure(value=max_fps)
                    
                #Widgets
                console.delete(1.0, tk.END)
                #BENCHMARK
                console.insert(tk.END, f"Stats:\n FPS: {str(int(fps))} || CPU: {str(cpu)} || RAM: {str(ram)} \n\n")
                
                console.insert(tk.END, "Detections:\n")
                for box in detections.boxes:
                    coords = box.xyxy[0].tolist()
                    coords = [int(coord) for coord in coords]
                    class_id = box.cls[0].item()
                    conf = box.conf[0].item()
                    
                    if conf > 0.5:
                        color = (0, 255, 0)
                        cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), color, 2)
                        
                        #DETECTIONS
                        console.insert(tk.END, f"{class_id}, {detections.names[int(class_id)]}, {conf}\n")
                        
                # cpu_meter.configure(amountused=int(psutil.cpu_percent()))
                # ram_meter.configure(amountused=int(psutil.virtual_memory().percent))
                
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                canvas.img = photo
                canvas.create_image(0, 0, anchor=tk.NW, image=photo)          

            else:
                stop_webcam()
                console.delete(1.0, tk.END)
        canvas.after(10, update_canvas)

# Function to quit the application
def quit_app():
    stop_webcam()
    root.quit()
    root.destroy()



    # Create the main Tkinter window
    # global root  
root = ttk.Window(themename = 'darkly')
style = root.style
root.title("YoloV8 Object Detection Model Tester")
root.iconbitmap(icon)

#Menu
menu = tk.Menu(root)

#Style Menu
file_menu = tk.Menu(menu, tearoff=False)
colorstyle = tk.StringVar(value='dark')
file_menu.add_checkbutton(label='Light', onvalue='light', offvalue='dark', variable=colorstyle, command=change_lighing)
file_menu.add_checkbutton(label='Dark', onvalue='dark', offvalue='light', variable=colorstyle, command=change_lighing)
menu.add_cascade(label='Style',menu=file_menu)

root.config(menu=menu)

# Create a Canvas widget to display the webcam feed or video
canvas = tk.Canvas(root, width=640, height=480)
canvas.grid(row=0,column=0,rowspan=2)

#Dashboard
dashboard = ttk.Frame(root)
dashboard.grid(row=0,column=1)

# Create an Console widget to display the detection results
console = tk.Text(root, width=35, font=(None,16))
console.grid(row=0,column=1,rowspan=3)

# Create a frame to hold the buttons
button_frame = ttk.Frame(root)
button_frame.grid(row=2,column=0,ipady=2)


# Create a "Select File" button to choose a video file
file_button = ttk.Button(button_frame, text="Select File", bootstyle="success-outline", command=select_file)
file_button.grid(row=0,column=0, padx= 5, columnspan=1)

# Create a "Pause/Resume" button to pause or resume video
pause_button = ttk.Button(button_frame, text="Pause/Resume", bootstyle="info-outline", command=pause_resume_video)
pause_button.grid(row=0,column=1, padx= 5, columnspan=1)

# Create a "Stop" button to stop the webcam feed
stop_button = ttk.Button(button_frame, text="Stop", bootstyle="warning-outline", command=stop_webcam)
stop_button.grid(row=0,column=3, padx= 5, columnspan=1)

# Create a "Quit" button to close the application
quit_button = ttk.Button(button_frame, text="Quit", bootstyle="danger", command=quit_app)
quit_button.grid(row=0,column=5, padx= 5, columnspan=1)

# Display an initial image on the canvas (replace 'initial_image.jpg' with your image)
change_lighing()

def main():
    root.mainloop()
    # Start the Tkinter main loop
    
if __name__ == "__main__":
    main()
