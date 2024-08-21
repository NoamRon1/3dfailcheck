import sensor, image
import time
import smtplib
import base64
from i2c_lcd import I2cLcd
from machine import I2C, Pin, UART
from fpioa_manager import fm
from board import board_info

# -----------------------------------------#
scl = 22
sda = 21
enc_button_pin = 0
ok = False  # encoder will change it
error = False  # if the system detect an error will be True


# -----------------------------------------#

def irq_change():
    global ok
    ok = True
    print("OK was set to True")


# -----------------------------------------#
enc_button = Pin(enc_button_pin, Pin.IN, Pin.PULL_UP)
enc_button.irq(trigger=Pin.IRQ_FALLING, handler=irq_change)


# -----------------------------------------#

def lcd_setup():
    global scl, sda
    i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=400000)
    i2c_addr = 0x27
    lcd = I2cLcd(i2c, i2c_addr, 2, 16)
    lcd.clear()
    global lcd


def file_list(file_list):
    global ok
    file_index = 0  # encoder will change it
    while not ok:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.write(file_list[file_index])
        print(file_list[file_index])
        time.sleep(.1)
    ok = False
    return file_list[file_index]


def image_check():
    ImagePaths = ["path1", "path2", "path3"]
    diffs = []
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=2000)
    sensor.set_auto_gain(True)
    sensor.set_auto_whitebal(True)
    print("camera setup complited")
    img_camera = sensor.snapshot()
    img_camera.save("camera_img.jpg")
    for path in ImagePaths:
        img_reference = image.Image(path)
        diff = img_camera.difference(img_reference)
        similarity_score = 100 - diff.get_hist().mean()
        diffs.append(similarity_score)
        print(f"Image {ImagePaths.index(path)}'s similarity_score is {similarity_score}")
    for diff in diffs:  # this is only because I want it to finish scaning and compering all of the photos
        if diff >= 80:
            return True
    return False


def qr_check():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=2000)
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    fm.register(board_info.PIN15, fm.fpioa.UART1_TX)
    fm.register(board_info.PIN17, fm.fpioa.UART1_RX)
    uart_A = UART(UART.UART1, 115200, 8, None, 1, timeout=1000, read_buf_len=4096)

    global lcd
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.write("show your details qr-code")
    lcd.move_to(0, 1)
    lcd.write("to the camera")
    print("show your details qr-code to the camera.\nusername, printname, user_email")

    while True:
        img = sensor.snapshot()
        res = img.find_qrcodes()
        if len(res) > 0:
            qr_data = res[0].payload()
            print("QR Code Data:", qr_data)
            uart_A.write(qr_data)
            break
        time.sleep(0.5)
    return qr_data.split(",")


def send_email_with_attachment(user_name, print_name, recipient_email):
    # Read the attachment file (JPEG) and encode it in base64
    attachment_path = "camera_img.jpg"
    sender_email = 'noam.ron@matics.live'  # Replace with your email
    sender_password = ''  # Replace with your password
    printer_name = "UltiShmulker"
    body = f"hello {user_name}, we are very sorry to tell you that the print {print_name}, you printed at {printer_name} failed.\n please check the printer and cancel it if needed.\n the image of the print is attached.\n if the print is ok please send us feedback for improving the sevice at noam2009r@gmail.com"
    subject = 'Print Failed'

    with open(attachment_path, 'rb') as attachment_file:
        attachment_data = attachment_file.read()
        encoded_attachment = base64.b64encode(attachment_data).decode()

    # Create the email headers
    headers = [
        f"From: {sender_email}",
        f"To: {recipient_email}",
        f"Subject: {subject}",
        "MIME-Version: 1.0",
        "Content-Type: multipart/mixed; boundary=BOUNDARY"
    ]

    # Email body
    message_body = [
        "--BOUNDARY",
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
        body,
        "",
        "--BOUNDARY",
        "Content-Type: image/jpeg; name=\"attachment.jpg\"",
        "Content-Transfer-Encoding: base64",
        "Content-Disposition: attachment; filename=\"attachment.jpg\"",
        "",
        encoded_attachment,
        "",
        "--BOUNDARY--"
    ]

    # Combine headers and body
    email_message = "\r\n".join(headers + [""] + message_body)

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, email_message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email:\n{e}")


def choose_time():
    global ok
    minutes = 0  # encoder will change it
    while not ok:
        lcd.clear()
        lcd.move_to(6, 0)
        lcd.write("print time:")
        lcd.move_to(4, 1)
        lcd.write(f"{minutes // 60}:{minutes % 60}")
    ok = False
    return minutes


def abort_confirmation():
    global ok
    index = 1  # encoder spin will change it
    while not ok:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.write("are you sure?")
        lcd.move_to(1, 1)
        if (index % 2 == 0):
            lcd.write("{yes}      no")
        else:
            lcd.write("yes      {no}")
    ok = False
    if (index % 2 == 0):
        return True
    else:
        return False


def run():
    user = qr_check()
    minutes = choose_time()
    start_time = time.time()
    global ok, error
    while not ok and ((time.time() - start_time) / 60 < minutes):
        lcd.clear()
        lcd.move_to(3, 0)
        lcd.write("Working. Click to abort")
        lcd.move_to(0,1)
        lcd.write(int(((time.time()-start_time)/60*100/minutes)/16)*"#")
        if image_check():
            error = True
            break
    ok = False
    if error:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.write("Error! Stop the print")
        lcd.move_to(0, 1)
        lcd.write("as soon as possible")
        send_email_with_attachment(user[0], user[1], user[2])
    else:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.write("Print Finished")


def begin():
    pass
