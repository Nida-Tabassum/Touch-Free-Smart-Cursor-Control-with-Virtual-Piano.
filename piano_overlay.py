import cv2

def draw_piano(img, active_notes):
    key_width = 40
    key_height = 120
    x_offset = 10
    y_offset = img.shape[0] - key_height - 10

    # White keys: C4 (60) to B4 (71)
    white_notes = list(range(60, 72))
    note_labels = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] * 2  # 2 octaves

    # Draw white keys with labels
    for i, note in enumerate(white_notes):
        x = x_offset + i * key_width
        color = (180, 220, 255) if note in active_notes else (255, 255, 255)
        cv2.rectangle(img, (x, y_offset), (x + key_width - 1, y_offset + key_height), color, -1)
        cv2.rectangle(img, (x, y_offset), (x + key_width - 1, y_offset + key_height), (0, 0, 0), 1)

        # Draw note label
        label = note_labels[i % 7]
        cv2.putText(img, label, (x + 10, y_offset + key_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # Black keys and their relative positions
    black_notes = {
        61: 0.75,  # C#4
        63: 1.75,  # D#4
        66: 3.75,  # F#4
        68: 4.75,  # G#4
        70: 5.75   # A#4
    }

    for note, pos in black_notes.items():
        x = x_offset + int(pos * key_width)
        if note in active_notes:
            color = (80, 80, 255)
        else:
            color = (0, 0, 0)
        cv2.rectangle(img, (x, y_offset), (x + key_width // 2, y_offset + key_height // 2), color, -1)

    return img
