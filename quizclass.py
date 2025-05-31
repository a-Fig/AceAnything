from typing import List, TypedDict, Callable, Tuple
import random
import re
import json
import pypdf
import math

import chatapi
import questionclass as qc
import tooled_llm as llm

print("quizclass.py")

class TutorLLM:
    def __init__(self, source_material: str,
                 additional_direction: str = "None",
                 model: str = "gemini-2.0-flash",
                 session_message_queue_ref: [List[str]] = None):
        self.source_material = source_material
        self._session_message_queue_ref = session_message_queue_ref

        tutor_tools: List[llm.Toolwrapper] = [
            llm.Toolwrapper("send_message", TutorLLM.send_message if session_message_queue_ref is None else self._send_message_to_user_session, """ # TutorLLM.send_message if session_message_queue_ref is None else self._send_message_to_user_session
            Action name: "send_message"
            Arguments: list of messages
            Purpose: Sends 1 or more message to the user. Break up long messages with '\\n'. This is the only way you are able to communicate with users
            Returns: conformation with Success or Fail
            """),
            llm.Toolwrapper("get_source_material", self.get_source_material, """
            Action name: "get_source_material"
            Arguments: empty list
            Purpose: Use to scan the source material for any information you need to look for.
            Returns: a copy of the source material you were told to review at the beginning
            """)
        ]

        self.Tutor: llm.ToolLLM = llm.ToolLLM(tool_objects=tutor_tools,
                                              model=model,
                                              directions=f"""
            You are the Tutor. Review the source material below and get ready to assist students.
            ####################  KNOWLEDGE  ####################
            {self.source_material}

            ####################  HANDLING INCORRECT ANSWERS (Primary Task)  #########################
            # When the user provides an incorrect answer, the input will contain:
            # Question:      ```{{{{question}}}}```
            # Wrong answer:  ```{{{{student_answer}}}}``` 
            # Correct answer ```{{{{correct_answer}}}}```  
            # Explanation:   ```{{{{explanation}}}}``` (This is the pre-defined explanation for the question)
            #
            # Your task for an incorrect answer:
            # 1. Identify the student's key error.
            # 2. Explain why their answer is wrong and why the correct answer is right, using the provided Explanation as a basis but elaborating if needed.
            # 3. Use the 'INITIAL RESPONSE FORMAT' below for this.
            # 4. End with an engaging follow-up question.
            # 5. CRITICAL: You MUST use the 'send_message' action for your entire response.

            ####################  INITIAL RESPONSE FORMAT (For Incorrect Answers) #######
            # (Content for 'send_message' action when student is incorrect)
            # (label {{{{correct_letter}}}} unless true/false question, then say true / false)
            # Correct answer: {{{{correct_letter}}}}  \\n  
            # {{{{student_letter}}}} is wrong – << concise factual error in student's choice (max 15 words) >>.  \\n 
            # {{{{correct_letter}}}} is right – << concise core fact for correct choice (max 15 words) >>.   \\n
            # << Elaborate on the provided 'Explanation' or add more context. Aim to teach. (max 75 words) >>
            # << Optional: related fun fact or mnemonic >> \\n
            # << Engaging follow-up question (e.g., "Does that make sense?", "Want a tip to remember this?") >>

            ####################  HANDLING CORRECT ANSWERS (Context Update) #########################
            # Sometimes, you'll receive a prompt starting with "Context: The student just answered...correctly."
            # This is for your information. 
            # *DO NOT* send a message to the user in response to this context update unless explicitly asked to in the context message.
            # Simply update your understanding of the student's progress and be ready for their next question.

            ####################  GENERAL FOLLOW-UP QUERIES & CONVERSATION #########################
            # When the user sends a message beginning with "User follow-up:", or asks a general question, 
            # or asks a question after getting an answer correct:
            # 1. Understand their query in the context of the source material and recent interactions (if any).
            # 2. Provide a comprehensive, informative, and helpful answer.
            # 3. Speak like your having a conversation with a friend.
            # 4. There is no rigid format for these responses, but always be clear, helpful, and concise.
            # 5. Aim for responses that are less then 200 words, with a max word count up to 500 words.
            # 6. If the user's query is vague, you can ask for clarification.
            # 7. If their query relates to a previous question, use your knowledge of the source material to elaborate.
            # 8. Use new lines ('\n') often to organize your response and improve readability.
            # 9. CRITICAL: You MUST use the 'send_message' action for your entire response.

            ####################  RESPONSE CONSTRAINTS (Apply to ALL messages sent to user) ##############
            # • CRITICAL: Your entire output, including explanations and any follow-up questions, MUST be sent as a list of strings within the 'args' of a 'send_message' action. Example: {{"action": "send_message", "args": ["Your full explanation here..."]}}
            # • Use new lines ('\n') often to organize your response and improve readability.
            # • No chit-chat, praise (e.g., "Good job!"), or filler unless it's a natural part of a conversational follow-up.
            # • Avoid simply stating 'the material says x'; aim to teach understanding.
            # • If referring to MCQ/TFQ options, use their letter if available, otherwise explain clearly.

            ####################  Additional Direction  ##############
        """ + additional_direction)

    def send_message(messages: List[str]) -> Tuple[bool, str]:
        if len(messages) == 0:
            return True, "error: empty message list"

        for msg in messages:
            lines = msg.split('\n')
            for line in lines:
                print(f"   {line}")
        return False, "Message sent"

    def _send_message_to_user_session(self, messages: List[str]) -> Tuple[bool, str]:
        """Appends messages from the LLM to the session-specific queue."""

        if self._session_message_queue_ref is None:
            print("CRITICAL: TutorLLM._send_message_to_user_session called but _session_message_queue_ref is None.")
            return True, "Error: Message queue not configured for this session. LLM cannot send message."

        if not isinstance(messages, list):
            print(f"Error: 'messages' argument must be a list of strings, got {type(messages)}")
            return True, "Error: 'messages' argument must be a list of strings."

        if not messages:
            # print("Warning: Empty messages list provided") # Keep this for now as it's useful
            return False, "No messages provided to send."

        for msg_index, msg_content in enumerate(messages):
            if isinstance(msg_content, str) and msg_content.strip():
                paragraphs = msg_content.split('\n\n')
                for para_index, paragraph in enumerate(paragraphs):
                    paragraph_stripped = paragraph.strip()
                    if paragraph_stripped:
                        self._session_message_queue_ref.append(paragraph_stripped)
            else:
                # Consider if this print is necessary or too verbose for normal operation
                # print(f"Skipping non-string or empty message content: {msg_content}")
                pass # Simply skip non-string or empty content

        return False, "Message(s) successfully queued for user."

    def get_source_material(self, arg: List[str]) -> Tuple[bool, str]:
        return True, self.source_material

    def prompt(self, message: str):
        # Call the ToolLLM's prompt method
        self.Tutor.prompt(message)


class Quiz:
    """
    Constructing a Quiz automatically spins up a ToolLLM (Gemini-Flash)
    that can:
      • build_section – create a new section
      • build_mcq / build_tfq / build_frq – add a question to a section

    Gemini NEVER prints the questions; it only calls tools.
    """

    class Section:
        def __init__(self, name: str):
            self.name = name
            self.questions: List[qc.Question] = []

        def __getitem__(self, key):
            return self.questions[key]

        def __setitem__(self, key, value):
            self.questions[key] = value

        def __len__(self):
            return len(self.questions)

    @classmethod
    def from_dict(cls, data):
        """
        Create a Quiz instance from a dictionary representation.
        """
        section_bank = []
        # Load title from the dict, default to empty string if not present
        title = data.get('title', '') 
        quiz = cls(section_bank=section_bank, source_material=data.get('source_material', ''), title=title)

        for section_data in data.get('sections', []):
            section = cls.Section(name=section_data.get('name', 'Uncategorized'))

            # Process questions in this section
            for q_data in section_data.get('questions', []):
                q_type = q_data.get('type')
                question = q_data.get('question', '')
                explanation = q_data.get('explanation', '')
                weight = float(q_data.get('weight', 1.0))

                if q_type == 'ShortAnswer':
                    correct_answer = q_data.get('correct_answer', [])
                    grading_instructions = q_data.get('grading_instructions', '')
                    q = qc.ShortAnswer(question, correct_answer, explanation, grading_instructions, weight)
                    section.questions.append(q)

                elif q_type == 'MultipleChoice':
                    correct_answers = q_data.get('correct_answers', [])
                    wrong_answers = q_data.get('wrong_answers', [])
                    q = qc.MultipleChoice(question, correct_answers, wrong_answers, explanation, weight)
                    section.questions.append(q)

                elif q_type == 'TrueFalseQuestion':
                    correct_answers = q_data.get('correct_answers', [])
                    wrong_answers = q_data.get('wrong_answers', [])
                    q = qc.TrueFalseQuestion(question, correct_answers, wrong_answers, explanation, weight)
                    section.questions.append(q)

            quiz.section_bank.append(section)

        return quiz

    def to_dict(self):
        """
        Convert the Quiz instance to a dictionary representation.
        """
        result = {
            'title': self.title, # Add title to the dictionary
            'source_material': self.source_material,
            'sections': []
        }

        for section in self.section_bank:
            section_data = {
                'name': section.name,
                'questions': []
            }

            for question in section.questions:
                q_data = {
                    'question': question.question,
                    'explanation': question.explanation,
                    'weight': question.weight
                }

                if isinstance(question, qc.ShortAnswer):
                    q_data['type'] = 'ShortAnswer'
                    q_data['correct_answer'] = question.correct_answer
                    q_data['grading_instructions'] = getattr(question, 'grading_instructions', '')

                elif isinstance(question, qc.TrueFalseQuestion):
                    q_data['type'] = 'TrueFalseQuestion'
                    q_data['correct_answers'] = question.correct_answer
                    q_data['wrong_answers'] = question.wrong_answers

                elif isinstance(question, qc.MultipleChoice):
                    q_data['type'] = 'MultipleChoice'
                    q_data['correct_answers'] = question.correct_answer
                    q_data['wrong_answers'] = question.wrong_answers

                section_data['questions'].append(q_data)

            result['sections'].append(section_data)

        return result

    def __init__(self, section_bank: List[Section], source_material: str = "", title: str = "Untitled Quiz", print_debug: bool = False, model="gemini-2.0-flash"):
        self.section_bank: List[Quiz.Section] = section_bank
        self.source_material = source_material
        self.title = title # Initialize title
        self.print_debug = print_debug
        self.model = model
        self.Tutor: TutorLLM = None
        self.size = None
        self.size = self.get_total_question_count()

    def get_total_question_count(self) -> int:
        """Calculates the total number of questions in the quiz across all sections."""
        if self.size is not None:
            return self.size
        count = 0
        for section in self.section_bank:
            count += len(section.questions)
        return count

    # usage
    def pick_question(self, is_first_question: bool = False) -> Tuple[int, int]:
        """
        Choose a question using each item's weight, but return *indices*
        (category_index, question_index) so the caller can fetch it later
        with `get_question`.

        If is_first_question is True, it will try to avoid picking a ShortAnswer question.

        Example
        -------
        cat_i, q_i = pick_question()
        question_obj = get_question(cat_i, q_i)

        Raises
        ------
        ValueError
            If there are no sections or no questions in any section.
        """
        if not self.section_bank:
            raise ValueError("Quiz has no sections")
        if not any(len(section) > 0 for section in self.section_bank):
            raise ValueError("Quiz has no questions in any section")

        eligible_questions_with_indices = []
        for i, section in enumerate(self.section_bank):
            for j, question in enumerate(section.questions):
                if is_first_question:
                    if not isinstance(question, qc.ShortAnswer):
                        eligible_questions_with_indices.append(((i, j), question))
                else:
                    eligible_questions_with_indices.append(((i, j), question))
        
        # Fallback if only ShortAnswer questions exist or no non-ShortAnswer questions were found for the first question
        if is_first_question and not any(not isinstance(q_tuple[1], qc.ShortAnswer) for q_tuple in eligible_questions_with_indices):
            print("Warning: First question preference for non-ShortAnswer could not be met. Picking any question.")
            eligible_questions_with_indices = [] # Reset to consider all questions
            for i, section in enumerate(self.section_bank):
                for j, question in enumerate(section.questions):
                    eligible_questions_with_indices.append(((i, j), question))

        if not eligible_questions_with_indices:
             # This should ideally not be reached if the initial checks pass and fallback works
            raise ValueError("No eligible questions found to pick from.")

        # Create a flat list of (category_idx, question_idx) tuples and corresponding weights
        # for the eligible questions.
        
        # We need to re-think the weighting if we filter.
        # For simplicity now, if filtering, we'll pick uniformly from the filtered list.
        # A more sophisticated approach would re-distribute weights.

        if is_first_question and any(not isinstance(q_tuple[1], qc.ShortAnswer) for q_tuple in eligible_questions_with_indices):
             # Filter again to be sure we are only picking from non-short answer if available
            non_short_answer_questions = [
                item for item in eligible_questions_with_indices if not isinstance(item[1], qc.ShortAnswer)
            ]
            if non_short_answer_questions: # If there are non-short-answer questions, pick from them
                # Uniform random choice among non-short-answer questions for the first question
                chosen_item_indices, _ = random.choice(non_short_answer_questions)
                return chosen_item_indices # (cat_idx, q_idx)
            # If, after filtering, no non-short-answer questions remain (shouldn't happen if logic is right),
            # fall through to original weighted logic below. This is a safeguard.


        # Original weighted picking logic (applied if not first question or if fallback needed)
        # This part needs to map flat indices back to sections or pick section first then question.
        # Let's stick to the original two-step weighted picking if not is_first_question or if no non-SA found.
        
        # 1) pick a category, weighted by its average question weight
        category_weights = [self._average_section_weight(cat, is_first_question) for cat in self.section_bank]
        
        valid_sections_indices = [i for i, weight in enumerate(category_weights) if weight > 0]
        if not valid_sections_indices:
             # This case implies that if is_first_question is true, all sections might only contain short answers
             # or are empty.
            if is_first_question: # Attempt to pick any question if the preferred type isn't available
                print("Warning: Could not find non-ShortAnswer questions in any section for the first question. Picking any question.")
                return self.pick_question(is_first_question=False) # Fallback to pick any type
            raise ValueError("No valid sections with eligible questions found.")


        valid_weights = [category_weights[i] for i in valid_sections_indices]
        
        chosen_cat_idx = random.choices(
            population=valid_sections_indices,
            weights=valid_weights,
            k=1
        )[0]

        # 2) pick a question inside that category, weighted by its own weight
        questions_in_chosen_cat = self.section_bank[chosen_cat_idx]
        
        eligible_q_in_cat_with_original_idx = []
        for original_q_idx, q_obj in enumerate(questions_in_chosen_cat.questions):
            if is_first_question:
                if not isinstance(q_obj, qc.ShortAnswer):
                    eligible_q_in_cat_with_original_idx.append((q_obj, original_q_idx))
            else:
                eligible_q_in_cat_with_original_idx.append((q_obj, original_q_idx))

        if not eligible_q_in_cat_with_original_idx:
            # This means the chosen category only has short answer questions, and it's the first question.
            # We should have been caught by the valid_sections_indices check or the initial attempt.
            # As a robust fallback, pick any question from the quiz without the first_question constraint.
            print(f"Warning: Section {chosen_cat_idx} has no non-ShortAnswer questions for the first question. Picking any type of question.")
            return self.pick_question(is_first_question=False)


        question_objects = [item[0] for item in eligible_q_in_cat_with_original_idx]
        original_indices = [item[1] for item in eligible_q_in_cat_with_original_idx]
        
        question_weights = [q.weight for q in question_objects]
        
        # random.choices returns a list, so take the first element
        chosen_q_local_idx_in_eligible = random.choices(
            population=range(len(question_objects)),
            weights=question_weights,
            k=1
        )[0]
        
        # Map back to original index in the section
        final_q_idx_in_section = original_indices[chosen_q_local_idx_in_eligible]

        return chosen_cat_idx, final_q_idx_in_section

    def _average_section_weight(self, section: Section, is_first_question: bool) -> float:
        questions_to_consider = []
        if is_first_question:
            for q in section.questions:
                if not isinstance(q, qc.ShortAnswer):
                    questions_to_consider.append(q)
            if not questions_to_consider: # If section only has short answers (or is empty)
                return 0.0 # This section won't be picked if we need non-short answer
        else:
            questions_to_consider = section.questions

        if not questions_to_consider:
            return 0.0
        
        current_sum = sum(q.weight for q in questions_to_consider)
        return current_sum / len(questions_to_consider)

    def get_question(self, cat_idx, q_idx) -> qc.Question:
        self.section_bank[cat_idx][q_idx].quiz_size = self.size
        return self.section_bank[cat_idx][q_idx]

    def get_tutor(self, session_message_queue_ref=None):
        if self.Tutor is None:
            self.Tutor = TutorLLM(
                source_material=self.source_material,
                model=self.model,
                session_message_queue_ref=session_message_queue_ref
            )
        return self.Tutor

def generate_ai_quiz(source_material: str, quiz_title: str = "AI Generated Quiz", quiz_size: int = None, print_debug: bool = False, model="gemini-2.0-flash"):
    """
    Generates a quiz using AI based on the provided source material.

    Args:
        source_material: The text content to generate questions from
        quiz_title: The desired title for the generated quiz.
        quiz_size: The target number of questions to generate
        print_debug: Whether to print debug information
        model: The AI model to use for generation
    """
    section_bank: List[Quiz.Section] = []

    def suggested_quiz_size(source: str, k: float = 0.35, q_min: int = 6, q_max: int = 30) -> int:
        """
        • Let n = number of *words* in the source.
        • Use √n so growth is sub-linear.
        • Scale by k, clamp to [q_min, q_max].
        """
        n_words = len(source.split())
        size = int(k * math.sqrt(n_words))
        return max(q_min, min(size, q_max))

    def _get_section(idx: int) -> Quiz.Section:
        if idx < 0 or idx >= len(section_bank):
            raise IndexError(f"Section index {idx} out of range.")
        return section_bank[idx]

    # ---------- TOOL IMPLEMENTATIONS ----------
    def build_section(arg: List[str]) -> Tuple[bool, str]:
        if print_debug: print(f"adding section", end='')
        try:
            title = arg[0]
            section_bank.append(Quiz.Section(title))
            idx = len(section_bank) - 1
            if print_debug: print(f", '{title}'")
            return True, f"Section #{idx} '{title}' created"
        except Exception as e:
            if print_debug: print()
            return True, f"Error building section, build_section({arg}) -> '{e}'"

    def build_mcq(arg: List[str]) -> Tuple[bool, str]:
        if print_debug: print(f"adding question")
        try:
            sec_idx = int(arg[0])
            question_text = arg[1]
            
            # Process correct answers
            correct_answers_raw = arg[2].split(',')
            correct = []
            for item_str in correct_answers_raw:
                stripped_item = item_str.strip()
                if stripped_item.startswith('('):
                    stripped_item = stripped_item[1:]
                if stripped_item.endswith(')'):
                    stripped_item = stripped_item[:-1]
                correct.append(stripped_item)
            
            # Process wrong answers
            wrong_answers_raw = arg[3].split(',')
            wrong = []
            for item_str in wrong_answers_raw:
                stripped_item = item_str.strip()
                if stripped_item.startswith('('):
                    stripped_item = stripped_item[1:]
                if stripped_item.endswith(')'):
                    stripped_item = stripped_item[:-1]
                wrong.append(stripped_item)
            
            explanation = arg[4]

            q = qc.MultipleChoice(question_text, correct, wrong, explanation)
            _get_section(sec_idx).questions.append(q)
            return True, f"question #{len(_get_section(sec_idx).questions)}, '{question_text}', was added to section {sec_idx}"
        except Exception as e:
            return True, f"Error in build_mcq({arg}) -> '{e}'"

    def build_tfq(arg: List[str]) -> Tuple[bool, str]:
        if print_debug: print(f"adding question")
        try:
            sec_idx = int(arg[0])
            question_text = arg[1]
            
            # Process correct answer (arg[2])
            correct_raw = arg[2].strip()
            if correct_raw.startswith('('):
                correct_raw = correct_raw[1:]
            if correct_raw.endswith(')'):
                correct_raw = correct_raw[:-1]
            correct_answer = [correct_raw]

            # Process wrong answer (arg[3])
            wrong_raw = arg[3].strip()
            if wrong_raw.startswith('('):
                wrong_raw = wrong_raw[1:]
            if wrong_raw.endswith(')'):
                wrong_raw = wrong_raw[:-1]
            wrong_answer = [wrong_raw]

            explanation = arg[4]

            q = qc.TrueFalseQuestion(question_text, correct_answer, wrong_answer, explanation)
            _get_section(sec_idx).questions.append(q)
            return True, f"question #{len(_get_section(sec_idx).questions)}, '{question_text}', was added to section {sec_idx}"
        except Exception as e:
            return True, f"Error in build_tfq({arg}) -> '{e}'"

    def build_frq(arg: List[str]) -> Tuple[bool, str]:
        if print_debug: print(f"adding question")
        try:
            sec_idx = int(arg[0])
            question_text = arg[1]
            
            # Process ideal answers
            ideal_answers_raw = arg[2].split(',')
            correct = []
            for item_str in ideal_answers_raw:
                stripped_item = item_str.strip()
                if stripped_item.startswith('('):
                    stripped_item = stripped_item[1:]
                if stripped_item.endswith(')'):
                    stripped_item = stripped_item[:-1]
                correct.append(stripped_item)
            
            explanation = arg[3]
            grading = arg[4] if len(arg) > 4 else "Be detailed and accurate."

            q = qc.ShortAnswer(question_text, correct, explanation, grading)
            _get_section(sec_idx).questions.append(q)
            return True, f"question #{len(_get_section(sec_idx).questions)}, '{question_text}', was added to section {sec_idx}"
        except Exception as e:
            return True, f"Error in build_frq({arg}) -> '{e}'"

    if quiz_size is None:
        quiz_size = suggested_quiz_size(source_material)

    # ---------- TOOL WRAPPERS ----------
    quiz_build_tools: List[llm.Toolwrapper] = [
        # ---- build_section ----
        llm.Toolwrapper(
            "build_section",
            build_section,
            """
            Action name: "build_section"
            Args:
              [0] Section title   str
            Returns string:
              • "Section #<idx> '<title>' created" on success
              • "Error building section [...]"      on failure
            Purpose: Creates a new section. Sections are 0-indexed in the order created.
            """.strip()
        ),

        # ---- build_mcq ----
        llm.Toolwrapper(
            "build_mcq",
            build_mcq,
            """
            Action name: "build_mcq"
            Args (exact order):
              [0] Section index (int as string)       str e.g. "0"
              [1] Question text                       str
              [2] Correct answers – comma-separated   str e.g. "(Carbon dioxide)" {Do not put any parentheses or commas inside of the options themselves}
              [3] Wrong  answers  – comma-separated   str e.g. "(Oxygen), (Nitrogen)" {Do not put any parentheses or commas inside of the options themselves}
              [4] Explanation 1-2 sentences           str
            Returns string (to LLM):
              • "question '<text>' was added to section <idx>"
              • "Error in build_mcq([...]) '<err>'"
            Purpose: Adds a Multiple-Choice question to the specified section.
            """.strip()
        ),

        # ---- build_tfq ----
        llm.Toolwrapper(
            "build_tfq",
            build_tfq,
            """
            Action name: "build_tfq"
            Args (exact order):
              [0] Section index (int as string)       str
              [1] Statement text                      str
              [2] Correct answer "(True)" or "(False)"  str
              [3] Wrong   answer "(True)" or "(False)"  str
              [4] Explanation 1-2 sentences           str
            Returns string as in build_mcq.
            Purpose: Adds a True/False question to the specified section.
            """.strip()
        ),

        # ---- build_frq ----
        llm.Toolwrapper(
            "build_frq",
            build_frq,
            """
            Action name: "build_frq"
            Args (exact order):
              [0] Section index (int as string)       str
              [1] Question text                       str
              [2] Ideal answer(s) comma-separated     str e.g. "(ATP production), (Energy generation)" {Do not put any parentheses or commas inside of the options themselves}
              [3] Explanation 1-2 sentences           str
              [4] Grading instructions (optional)     str
            Returns string as in build_mcq.
            Purpose: Adds a short free-response question to the specified section.
            """.strip()
        ),
    ]

    # ---------- LLM WITH TOOLS ----------
    smart_quiz_builder = llm.ToolLLM(
        tool_objects=quiz_build_tools,
        model=model,
        directions=f"""
        You are an expert quiz-writer.

        **Workflow**  
        1. Create a section using *build_section* (e.g. "Basics", "Advanced", "Multiplication", "Road Signs").
        2. await confirmation  
        3. add a few questions. 
        4. await confirmation
        5. Add even more questions (optional)
        6. Repeat steps 1 through 5 until hitting about {quiz_size} total questions. You may create multiple questions and sections in the same turn for efficiency.
        7. STOP and return `[]`.

        once you have successfully made a few sections, 
        you can may start making many more sections and questions in a single turn.
        Especially if you are making a very large quiz. 
        You may add a question to ANY section you have already made.

        Target mix ≈ 50 % MCQ, 30 % TFQ, 20 % FRQ.  
        Free response questions should be a mix of 1 word responses, and 1-2 sentence responses. 
        Avoid free response questions that would require long answers unless you a have good reason to do it.
        Everything must be 100 % supported by SOURCE MATERIAL; no duplicates.  
        Strictly follow each tool's arg format (section index first!).  
        After hitting about {quiz_size} total questions, STOP and return `[]`.

        ### EXAMPLES (copy the structure)
        build_section ["Foundations"]

        build_mcq ["0",
                   "What gas do plants absorb during photosynthesis?",
                   "(Carbon dioxide)",
                   "(Oxygen), (Nitrogen), (Hydrogen)",
                   "Plants use carbon dioxide to produce glucose during photosynthesis."]

        build_tfq ["1",
                   "The capital of France is Paris.",
                   "(True)",
                   "(False)",
                   "Paris is the capital and largest city of France."]

        build_frq ["1",
                   "Define osmosis.",
                   "(Movement of water across a semipermeable membrane from low solute concentration to high solute concentration)",
                   "Osmosis is passive diffusion of water.",
                   "Must mention water movement, semipermeable membrane, and concentration gradient."]
                    """.strip(),
        action_prompt=f"""
        Build the quiz based on the source material below.
        ### SOURCE MATERIAL ###
        {source_material}
        """.strip()
    )

    return Quiz(section_bank, source_material, title=quiz_title, print_debug=print_debug, model=model)


def openpdf(pdf_file_path) -> str:
    doc = pypdf.PdfReader(pdf_file_path)
    extracted_text = ""
    for page_num in range(len(doc.pages)):
        page = doc.pages[page_num].extract_text().replace('\n', ' ')
        extracted_text += f"-- Page {page_num + 1} --\n{page}\n"
    doc.close()
    return extracted_text

def print_quiz(quiz: Quiz):
    for section in quiz.section_bank:
        count = 0
        print(f"###\n{section.name}\n###")
        for q in section.questions:
            count += 1
            if isinstance(q, qc.MultipleChoice):
                print(f"question: {q.question}")
                print(f"correct: {q.correct_answer}")
                print(f"wrong: {q.wrong_answers}")
                print(f"explanation: {q.explanation}")
            elif isinstance(q, qc.ShortAnswer):
                print(f"question: {q.question}")
                print(f"explanation: {q.explanation}")
                print(f"grading_instructions: {q.grading_instructions}")
            print("=====")


def console_quiz(ai_quiz: Quiz):
    try:
        score: int = 0
        questions_answered: int = 0
        while True:
            cat_idx, q_idx = ai_quiz.pick_question()
            question: qc.Question = ai_quiz.get_question(cat_idx, q_idx)

            full_question = f"\n{question.build_question()}"
            print(full_question)

            questions_answered += 1

            user_message = input("enter choice>")
            if user_message == "stop":
                break

            grade, reason = question.grade_answer(user_message)
            if grade > 0.80:
                score += 1
                print(f"{score}/{questions_answered} - Correct! ",end='')
                if reason != "":
                    print(f"{grade * 100}% , {reason}", end='')
                print()
            else:
                print(f"{score}/{questions_answered} - Incorrect, entering chat with AI, type 'next' to move on to the next question")
                grader_response = f"Grader justification: {reason}" if reason != "" else ""
                ai_quiz.Tutor.prompt(f""" The user has answered a question incorrectly.
                Original Question: {full_question}
                Student's Incorrect Answer: {user_message}
                Question Explanation: {question.explanation}
                {grader_response}
                Send them a message to help them understand.
                """)
                user_message = input("respond>")
                while user_message != "next":
                    ai_quiz.Tutor.prompt(f"user response: '{user_message}'")
                    user_message = input("respond>")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == '__main__':

    soruce = openpdf("premade_quizzes/US Citizenship Test Knowledge Report_.pdf")
    ai_quiz = generate_ai_quiz(soruce, 20, print_debug=True, model="gemini-2.0-flash")

    print_quiz(ai_quiz)
