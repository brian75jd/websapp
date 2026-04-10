def get_room_name(user1,user2):
    users = sorted([str(user1.id),str(user2.id)])
    return f"chat_{users[0]}_{users[1]}"