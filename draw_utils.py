import cv2

def draw_text_box(img, text, position='top', text_color=(255, 255, 255), box_color=(0, 0, 0)):
    font_scale = 0.9
    thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)

    if position == 'top':
        org = (10, 40)
    elif position == 'middle':
        org = (int((img.shape[1] - text_size[0]) / 2), int((img.shape[0] + text_size[1]) / 2))
    else:
        org = (10, 40)

    top_left = (org[0] - 10, org[1] - text_size[1] - 10)
    bottom_right = (org[0] + text_size[0] + 10, org[1] + 10)
    cv2.rectangle(img, top_left, bottom_right, box_color, cv2.FILLED)
    cv2.putText(img, text, org, font, font_scale, text_color, thickness, cv2.LINE_AA)
