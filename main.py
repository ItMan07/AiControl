from HandsControl import AiHands

ai = AiHands(
    dist_to_click=50,
    camera_frame_width=1280,
    camera_frame_height=720,
    flip_code=1,
    camera_id=0,
)
ai.processing()
