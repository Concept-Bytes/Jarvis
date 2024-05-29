from db import insert_conversation, fetch_all_conversations

# Retrieve and display all records from the conversation table (optional)
conversations = fetch_all_conversations(limit=5)
for conversation in conversations:
    print(conversation)
