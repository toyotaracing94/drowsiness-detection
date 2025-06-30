
def to_connections(indices):
    return [(indices[i], indices[i+1]) for i in range(len(indices)-1)]

# ================================
# Facial Landmark Index Map (MediaPipe Face Mesh reference)
# ================================

# CONNECTIONS for drawing purpose
OUTER_LIPS_CONNECTIONS = [
    (61, 37), (37, 0), (0, 267), (267, 291),
    (291, 375), (375, 314), (314, 17), (17, 84), (84, 146), (146, 61)
]

INNER_LIPS_CONNECTIONS = [
    (78, 82), (82, 13), (13, 312), (312, 415),
    (415, 308), (308, 317), (317, 14), (14, 87), (87, 95), (95, 78)
]

LEFT_EYE_CONNECTIONS = [
    (33, 160), (160, 159), (159, 158), (158, 133),
    (133, 155), (155, 153), (153, 145), (145, 144), (144, 33)
]

RIGHT_EYE_CONNECTIONS = [
    (362, 385), (385, 386), (386, 387), (387, 263),
    (263, 390), (390, 373), (373, 374), (374, 380), (380, 362)
]

LEFT_EYEBROW_CONNECTIONS = [
    (70, 63), (63, 105), (105, 66), (66, 107)
]

RIGHT_EYEBROW_CONNECTIONS = [
    (336, 296), (296, 334), (334, 293), (293, 300)
]

OUTER_FACE_CONNECTIONS = [
    (10, 338), (338, 297), (297, 332), (332, 284), (284, 251), (251, 389),
    (389, 356), (356, 454), (454, 323), (323, 361), (361, 288), (288, 397),
    (397, 365), (365, 379), (379, 378), (378, 400), (400, 377), (377, 152),
    (152, 148), (148, 176), (176, 149), (149, 150), (150, 136), (136, 172),
    (172, 58), (58, 132), (132, 93), (93, 234), (234, 127), (127, 162),
    (162, 21), (21, 54), (54, 103), (103, 67), (67, 109)
]


# POINTS for calculations
LEFT_EYE_POINTS = [
    33, 160, 158, 133, 153, 144
]

RIGHT_EYE_POINTS = [
    362, 385, 387, 263, 373, 380
]

OUTER_LIPS_POINTS = [
    61, 39, 0, 269, 291, 405, 17, 181
]

HEAD_POSE_POINTS = [
    1, 33, 61, 199, 263, 291
]

# ================================
# Hand Landmark Index Map (MediaPipe Hands reference)
# ================================

# CONNECTIONS for drawing purpose
HAND_CONNECTIONS = [
    # Thumb
    (0, 1), (1, 2), (2, 3), (3, 4),
    
    # Index finger
    (0, 5), (5, 6), (6, 7), (7, 8),
    
    # Middle finger
    (0, 9), (9, 10), (10, 11), (11, 12),
    
    # Ring finger
    (0, 13), (13, 14), (14, 15), (15, 16),
    
    # Pinky
    (0, 17), (17, 18), (18, 19), (19, 20)
]

# FINGER CONNECTION GROUPS
THUMB_CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 4)]
INDEX_FINGER_CONNECTIONS = [(0, 5), (5, 6), (6, 7), (7, 8)]
MIDDLE_FINGER_CONNECTIONS = [(0, 9), (9, 10), (10, 11), (11, 12)]
RING_FINGER_CONNECTIONS = [(0, 13), (13, 14), (14, 15), (15, 16)]
PINKY_FINGER_CONNECTIONS = [(0, 17), (17, 18), (18, 19), (19, 20)]

# POINTS for calculations (tips and base joints)
FINGER_TIPS_PINTS = [4, 8, 12, 16, 20]
FINGER_BASES_POINTS = [1, 5, 9, 13, 17]

# HAND CENTER for possible palm calculations
PALM_POINTS = [0, 1, 5, 9, 13, 17]

# Useful for finger orientation or gesture recognition
THUMB_POINTS = [1, 2, 3, 4]
INDEX_POINTS = [5, 6, 7, 8]
MIDDLE_POINTS = [9, 10, 11, 12]
RING_POINTS = [13, 14, 15, 16]
PINKY_POINTS = [17, 18, 19, 20]


# ================================
# Body Landmark Index Map (MediaPipe Hands reference)
# ================================

# CONNECTIONS for drawing purpose
TORSO_CONNECTIONS = [
    (11, 12), (12, 24), (24, 23), (23, 11),
]

BODY_POSE_FACE_CONNECTIONS = [
    (7, 3), (3, 2), (2, 1), (1, 0), 
    (0, 4), (4, 5), (5, 6), (6, 8)
]