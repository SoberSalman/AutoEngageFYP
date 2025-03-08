import os
import queue
import random
import re
import csv
import threading
from openvoicechat.utils import log_to_file

class UserInformation:
    """Class to track and store user information during a conversation"""
    def __init__(self):
        self.name = None
        self.age = None
        self.city = None
        self.zipcode = None
        self.interest_level = None
        self.additional_notes = []
        self.collection_complete = False
        
        # Track verification status for each field
        self.verified = {
            'name': False,
            'age': False,
            'city': False,
            'zipcode': False,
            'interest': False
        }
        
        # Track current verification field if any
        self.current_verification = None
        
    def is_complete(self):
        """Check if all required information has been collected and verified"""
        all_collected = (self.name and self.age and self.city and 
                     self.zipcode and self.interest_level is not None)
        
        all_verified = all(self.verified.values())
        
        return all_collected and all_verified
    
    def get_next_question(self):
        """Return the next question to ask based on missing information or verification needs"""
        # If we're currently verifying something, continue with that
        if self.current_verification:
            return self.current_verification
            
        # Check if any collected information needs verification
        if self.name and not self.verified['name']:
            self.current_verification = "verify_name"
            return "verify_name"
        
        if self.age and not self.verified['age']:
            self.current_verification = "verify_age"
            return "verify_age"
            
        if self.city and not self.verified['city']:
            self.current_verification = "verify_city"
            return "verify_city"
            
        if self.zipcode and not self.verified['zipcode']:
            self.current_verification = "verify_zipcode"
            return "verify_zipcode"
            
        if self.interest_level and not self.verified['interest']:
            self.current_verification = "verify_interest"
            return "verify_interest"
        
        # If everything collected is verified, check what's missing
        if not self.name:
            return "get_name"
        elif not self.age:
            return "get_age"
        elif not self.city:
            return "get_city"
        elif not self.zipcode:
            return "get_zipcode"
        elif self.interest_level is None:
            return "get_interest"
        else:
            return "complete"
            
    def update_from_message(self, message, field=None):
        """Try to extract information from user message"""
        # First, check for verification responses (yes/correct/right/etc.)
        message_lower = message.lower()
        is_confirming = any(word in message_lower for word in 
                           ["yes", "correct", "right", "yeah", "yep", "sure", "exactly"])
        
        # If the user is confirming and we're verifying something
        if is_confirming and self.current_verification:
            if self.current_verification == "verify_name":
                self.verified['name'] = True
            elif self.current_verification == "verify_age":
                self.verified['age'] = True
            elif self.current_verification == "verify_city":
                self.verified['city'] = True
            elif self.current_verification == "verify_zipcode":
                self.verified['zipcode'] = True
            elif self.current_verification == "verify_interest":
                self.verified['interest'] = True
                
            # Clear the current verification now that it's done
            self.current_verification = None
            return
            
        # If we're in verification mode but user didn't confirm, keep current mode
        # but don't mark as verified yet
        if self.current_verification and not is_confirming:
            # If they're correcting information, try to extract again
            if field == "get_name" or self.current_verification == "verify_name":
                # Simple name extraction - first word that's capitalized
                words = message.split()
                for word in words:
                    if len(word) > 1 and word[0].isupper() and word.isalpha():
                        self.name = word
                        break
            
            # Continue with verification rather than proceeding to next field
            return
        
        # Regular information extraction
        if field == "get_name" or field is None:
            # Simple name extraction - first word that's capitalized
            words = message.split()
            for word in words:
                if len(word) > 1 and word[0].isupper() and word.isalpha():
                    self.name = word
                    break
        
        if field == "get_age" or field is None:
            # Extract numbers that could be age (between 18-99)
            import re
            age_matches = re.findall(r'\b([1-9][0-9])\b', message)
            for match in age_matches:
                age = int(match)
                if 18 <= age <= 99:
                    self.age = age
                    break
        
        if field == "get_city" or field is None:
            # This would need more sophisticated processing in a real system
            # For now, assume the city is mentioned after "in" or "from"
            words = message.lower().split()
            for i, word in enumerate(words):
                if word in ["in", "from"] and i < len(words) - 1:
                    # Take the next word if it's capitalized in the original message
                    original_words = message.split()
                    if i+1 < len(original_words) and original_words[i+1][0].isupper():
                        self.city = original_words[i+1]
                        # Remove any punctuation
                        self.city = self.city.rstrip(',.!?')
                        break
        
        if field == "get_zipcode" or field is None:
            # Look for 5-digit numbers that could be zipcodes
            import re
            zip_matches = re.findall(r'\b(\d{5})\b', message)
            if zip_matches:
                self.zipcode = zip_matches[0]
        
        if field == "get_interest" or field is None:
            # Check for interest indicators
            message_lower = message.lower()
            if any(word in message_lower for word in ["yes", "interested", "sure", "definitely", "absolutely"]):
                self.interest_level = "Interested"
            elif any(word in message_lower for word in ["no", "not interested", "nope", "pass"]):
                self.interest_level = "Not interested"
            elif any(word in message_lower for word in ["maybe", "perhaps", "not sure", "think about"]):
                self.interest_level = "Maybe interested"

    def spell_name(self):
        """Return the name spelled out letter by letter"""
        if not self.name:
            return ""
        return "-".join(self.name)
        
    def format_zipcode_for_speech(self):
        """Format zipcode for speech (e.g., 46006 becomes 'four six zero zero six')"""
        if not self.zipcode:
            return ""
            
        digit_words = {
            '0': 'zero',
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine'
        }
        
        return " ".join(digit_words[digit] for digit in str(self.zipcode))

    def __str__(self):
        """Return a string representation of the collected information"""
        info = []
        if self.name:
            info.append(f"Name: {self.name}")
        if self.age:
            info.append(f"Age: {self.age}")
        if self.city:
            info.append(f"City: {self.city}")
        if self.zipcode:
            info.append(f"Zipcode: {self.zipcode}")
        if self.interest_level:
            info.append(f"Interest: {self.interest_level}")
        if self.additional_notes:
            info.append(f"Notes: {'; '.join(self.additional_notes)}")
        return ", ".join(info)


def run_chat_agent(
    mouth,
    ear,
    chatbot,
    minibot_args=None,
    verbose=True,
    stopping_criteria=lambda x: False,
    starting_message=True,
    logging_path="chat_log.txt",
    save_path="user_info.csv"
):
    """
    Enhanced chat function that acts as an agent to collect user information while introducing the company.
    
    Parameters:
    mouth - TTS component
    ear - STT component
    chatbot - LLM interface
    minibot_args - Organization and agent info
    save_path - Path to save the collected user information CSV
    """
    import os
    import csv
    import queue
    import threading
    
    # Initialize user information tracker
    user_info = UserInformation()
    
    # Set up system prompt for the agent
    agent_prompt = """You are a friendly sales agent for {organization_name}. Your goal is to:

1. Introduce the company and its offerings
2. Collect the following information from the user:
   - Name (confirm by spelling it out letter by letter)
   - Age
   - City
   - Zipcode (read back the numbers individually)
   - Whether they're interested in our services

IMPORTANT GUIDELINES:
- Begin with a brief introduction of who you are and what {organization_name} offers
- After collecting each piece of information, verify it by asking "Is that correct?"
- For names, spell out each letter (e.g., "S-a-l-m-a-n, is that right?")
- For zipcodes, read back each digit separately (e.g., "four six zero zero six")
- If asked about services, explain them briefly before returning to information collection
- Keep responses conversational and engaging
- After collecting all information, thank them and explain the next steps

Your first goal is to introduce yourself and then ask for their name."""

    # Set the system prompt in the chatbot
    agent_name = minibot_args.get("agent_name", "Agent")
    organization_name = minibot_args.get("organization_name", "Our Company")
    
    # Replace the system prompt with our agent prompt
    chatbot.messages = [{"role": "system", "content": agent_prompt.format(
        agent_name=agent_name,
        organization_name=organization_name
    )}]

    if starting_message:
        # Create a more comprehensive introduction that mentions the company and services
        product_desc = ""
        if minibot_args and "product_names" in minibot_args and minibot_args["product_names"]:
            product_desc = f", offering {minibot_args['product_names'][0]}"
            
        initial_message = f"Hello! I'm {agent_name} from {organization_name}{product_desc}. I'd like to assist you today by gathering some basic information. May I start by asking your name?"
        mouth.say_text(initial_message)

    pre_interruption_text = ""
    current_question_type = "get_name"
    introduction_given = False
    
    while True:
        user_input = pre_interruption_text + " " + ear.listen()

        if verbose:
            print("USER: ", user_input)
        if os.environ.get("LOGGING", 0):
            log_to_file(logging_path, "USER: " + user_input)
        
        # Check if this is a question about services/products
        lower_input = user_input.lower()
        is_product_question = any(word in lower_input for word in 
                               ["what", "service", "product", "offer", "provide", "sell", "about", "company"])
                               
        # Try to extract information from user input
        prev_info_state = str(user_info)
        user_info.update_from_message(user_input, current_question_type)
        
        # Determine the next question to ask
        current_question_type = user_info.get_next_question()
        
        # Generate agent response based on the conversation state
        if current_question_type == "complete" and not user_info.collection_complete:
            # All info collected, prepare wrap-up message
            user_info.collection_complete = True
            
            # Create a personalized closing message
            interest_text = ""
            if user_info.interest_level == "Interested":
                interest_text = "since you're interested in our services, "
            elif user_info.interest_level == "Maybe interested":
                interest_text = "while you consider our services, "
                
            product_mention = ""
            if minibot_args and "product_names" in minibot_args and minibot_args["product_names"]:
                product_mention = f" about our {minibot_args['product_names'][0]}"
            
            agent_message = f"Thank you {user_info.name}! I've got all your information. {interest_text}a sales representative will contact you soon{product_mention} to discuss your specific needs."
            
            # Add a message to chatbot context to generate a proper response
            chatbot.messages.append({"role": "user", "content": user_input})
            chatbot.messages.append({"role": "assistant", "content": agent_message})
            
            # Save collected information to CSV
            is_new_file = not os.path.exists(save_path)
            with open(save_path, 'a', newline='') as file:
                writer = csv.writer(file)
                if is_new_file:
                    writer.writerow(['Name', 'Age', 'City', 'Zipcode', 'Interest'])
                writer.writerow([
                    user_info.name, 
                    user_info.age, 
                    user_info.city, 
                    user_info.zipcode, 
                    user_info.interest_level
                ])
            
            # Speak the closing message
            mouth.say_text(agent_message)
            
            if verbose:
                print("BOT: ", agent_message)
                print("INFO COLLECTED: ", user_info)
            if os.environ.get("LOGGING", 0):
                log_to_file(logging_path, "BOT: " + agent_message)
                log_to_file(logging_path, "INFO COLLECTED: " + str(user_info))
            
            # End the conversation
            break
            
        # Check if user asked about products/services
        elif is_product_question:
            # Generate a response about products
            product_response = "Let me tell you about what we offer. "
            
            if minibot_args and "product_names" in minibot_args and len(minibot_args["product_names"]) > 0:
                for i, (name, desc) in enumerate(zip(minibot_args["product_names"], minibot_args["product_descriptions"])):
                    if i < 2:  # Limit to first 2 products to keep response manageable
                        product_response += f"Our {name} {desc[:100]} "
                        
            product_response += "Now, let's continue with your information. "
            
            # Add the question for the current information we need
            if current_question_type == "get_name":
                product_response += "What is your name?"
            elif current_question_type == "get_age":
                product_response += "What is your age?"
            elif current_question_type == "get_city":
                product_response += "What city do you live in?"
            elif current_question_type == "get_zipcode":
                product_response += "What is your zipcode?"
            elif current_question_type == "get_interest":
                product_response += "Are you interested in our services?"
            elif current_question_type.startswith("verify_"):
                # Handle verification cases
                field = current_question_type.split("_")[1]
                if field == "name":
                    product_response += f"So your name is {user_info.name}, spelled {'-'.join(user_info.name)}. Is that correct?"
                elif field == "age":
                    product_response += f"You're {user_info.age} years old. Is that right?"
                elif field == "city":
                    product_response += f"You live in {user_info.city}. Is that correct?"
                elif field == "zipcode":
                    digit_words = user_info.format_zipcode_for_speech()
                    product_response += f"Your zipcode is {digit_words}. Is that right?"
                elif field == "interest":
                    product_response += f"So you're {user_info.interest_level.lower()} in our services. Is that correct?"
            
            # Speak the response
            mouth.say_text(product_response)
            
            if verbose:
                print("BOT: ", product_response)
            if os.environ.get("LOGGING", 0):
                log_to_file(logging_path, "BOT: " + product_response)
                
        # Handle verification questions
        elif current_question_type.startswith("verify_"):
            field = current_question_type.split("_")[1]
            
            verify_question = ""
            if field == "name":
                name_spelled = "-".join(user_info.name)
                verify_question = f"So your name is {user_info.name}, spelled {name_spelled}. Is that correct?"
            elif field == "age":
                verify_question = f"You're {user_info.age} years old. Is that right?"
            elif field == "city":
                verify_question = f"You live in {user_info.city}. Is that correct?"
            elif field == "zipcode":
                digit_words = user_info.format_zipcode_for_speech()
                verify_question = f"Your zipcode is {digit_words}. Is that right?"
            elif field == "interest":
                verify_question = f"So you're {user_info.interest_level.lower()} in our services. Is that correct?"
                
            # Add verification message to context
            chatbot.messages.append({"role": "user", "content": user_input})
            chatbot.messages.append({"role": "assistant", "content": verify_question})
            
            # Speak the verification question
            mouth.say_text(verify_question)
            
            if verbose:
                print("BOT: ", verify_question)
            if os.environ.get("LOGGING", 0):
                log_to_file(logging_path, "BOT: " + verify_question)
                
        # Regular information collection       
        else:
            # Prepare the next question based on what information is missing
            next_question = ""
            
            # If this is the first interaction after starting message, make sure to introduce the company
            if not introduction_given and current_question_type == "get_name":
                introduction_given = True
                company_intro = ""
                
                if minibot_args and "organization_name" in minibot_args:
                    company_intro = f"Let me briefly tell you about {minibot_args['organization_name']}. "
                    
                    if "product_names" in minibot_args and len(minibot_args["product_names"]) > 0:
                        company_intro += f"We specialize in {minibot_args['product_names'][0]}"
                        
                        if "product_descriptions" in minibot_args and len(minibot_args["product_descriptions"]) > 0:
                            company_intro += f", which {minibot_args['product_descriptions'][0][:100]}"
                            
                company_intro += " Now, may I know your name?"
                next_question = company_intro
            elif current_question_type == "get_name":
                next_question = "Could you please tell me your name?"
            elif current_question_type == "get_age":
                next_question = f"Thanks{' ' + user_info.name if user_info.name else ''}! May I know your age?"
            elif current_question_type == "get_city":
                next_question = "What city do you live in?"
            elif current_question_type == "get_zipcode":
                next_question = "And what's your zipcode?"
            elif current_question_type == "get_interest":
                product_desc = ""
                if minibot_args and "product_names" in minibot_args and minibot_args["product_names"]:
                    product_desc = f" in our {minibot_args['product_names'][0]}"
                next_question = f"Are you interested{product_desc}?"
            
            # Add the conversation to the chatbot context
            chatbot.messages.append({"role": "user", "content": user_input})
            
            # If we extracted new information, acknowledge it
            if str(user_info) != prev_info_state:
                acknowledge = ""
                if user_info.name and current_question_type != "get_name":
                    acknowledge = f"Got it. "
                
                chatbot.messages.append({"role": "assistant", "content": acknowledge + next_question})
                
                # Use the chatbot to generate a response
                llm_output_queue = queue.Queue()
                interrupt_queue = queue.Queue()
                
                # Start LLM thread
                llm_thread = threading.Thread(
                    target=chatbot.generate_response_stream,
                    args=(user_input, llm_output_queue, interrupt_queue, minibot_args),
                )
                
                # Start TTS thread
                tts_thread = threading.Thread(
                    target=mouth.say_multiple_stream,
                    args=(llm_output_queue, ear.interrupt_listen, interrupt_queue),
                )
                
                llm_thread.start()
                tts_thread.start()
                
                llm_thread.join()
                tts_thread.join()
                
                if not interrupt_queue.empty():
                    pre_interruption_text = interrupt_queue.get()
                else:
                    pre_interruption_text = ""
                    
                response = llm_output_queue.get()
                
                if verbose:
                    print("BOT: ", response)
                if os.environ.get("LOGGING", 0):
                    log_to_file(logging_path, "BOT: " + response)
            else:
                # Direct question if we didn't extract information
                chatbot.messages.append({"role": "assistant", "content": next_question})
                
                # Use the chatbot to generate a response
                llm_output_queue = queue.Queue()
                interrupt_queue = queue.Queue()
                
                # Start LLM thread
                llm_thread = threading.Thread(
                    target=chatbot.generate_response_stream,
                    args=(user_input, llm_output_queue, interrupt_queue, minibot_args),
                )
                
                # Start TTS thread
                tts_thread = threading.Thread(
                    target=mouth.say_multiple_stream,
                    args=(llm_output_queue, ear.interrupt_listen, interrupt_queue),
                )
                
                llm_thread.start()
                tts_thread.start()
                
                llm_thread.join()
                tts_thread.join()
                
                if not interrupt_queue.empty():
                    pre_interruption_text = interrupt_queue.get()
                else:
                    pre_interruption_text = ""
                    
                response = llm_output_queue.get()
                
                if verbose:
                    print("BOT: ", response)
                if os.environ.get("LOGGING", 0):
                    log_to_file(logging_path, "BOT: " + response)