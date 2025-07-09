import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DSA Quiz: Become the King! 👑")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (200, 200, 200)
DARK_BLUE = (25, 25, 100)
YELLOW = (255, 215, 0)

# Fonts
title_font = pygame.font.Font(None, 60)
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Sound effects
pygame.mixer.init()
correct_sound = pygame.mixer.Sound("correct.wav") if os.path.exists("correct.wav") else None
wrong_sound = pygame.mixer.Sound("wrong.wav") if os.path.exists("wrong.wav") else None
click_sound = pygame.mixer.Sound("click.wav") if os.path.exists("click.wav") else None

# Game states
MAIN_MENU = 0
QUIZ = 1
RESULTS = 2

# Full set of questions
questions = [
    # Easy Questions
    {"id": 0, "question": "What is the time complexity of accessing an element in an array?", 
     "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "answer": "O(1)", 
     "explanation": "Arrays allow constant-time access using indexing."},

    {"id": 1, "question": "Which data structure uses LIFO (Last In, First Out)?", 
     "options": ["Queue", "Stack", "Heap", "Graph"], "answer": "Stack", 
     "explanation": "Stacks follow the LIFO principle where the last item added is removed first."},

    {"id": 2, "question": "What is the best-case time complexity of Bubble Sort?", 
     "options": ["O(n)", "O(n log n)", "O(n^2)", "O(1)"], "answer": "O(n)", 
     "explanation": "Bubble Sort runs in O(n) if the array is already sorted."},

    {"id": 3, "question": "Which of the following is a stable sorting algorithm?", 
     "options": ["QuickSort", "MergeSort", "HeapSort", "SelectionSort"], "answer": "MergeSort", 
     "explanation": "MergeSort maintains relative order of equal elements, making it stable."},

    {"id": 4, "question": "Which operation is the most expensive in a singly linked list?", 
     "options": ["Accessing an element", "Inserting at the head", "Deleting at the tail", "Reversing the list"], 
     "answer": "Accessing an element", "explanation": "Accessing an element takes O(n) in a singly linked list, as traversal is needed."},

    {"id": 5, "question": "What is the time complexity of searching in a balanced binary search tree (BST)?", 
     "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"], "answer": "O(log n)", 
     "explanation": "A balanced BST like AVL or Red-Black Tree allows logarithmic search time."},

    {"id": 6, "question": "Which of these is an example of a greedy algorithm?", 
     "options": ["Dijkstra’s Algorithm", "Merge Sort", "Floyd-Warshall Algorithm", "Depth-First Search"], 
     "answer": "Dijkstra’s Algorithm", "explanation": "Dijkstra’s Algorithm selects the shortest available path at each step, making it greedy."},

    {"id": 7, "question": "Which data structure is most efficient for implementing an Undo feature?", 
     "options": ["Queue", "Stack", "Linked List", "Array"], "answer": "Stack", 
     "explanation": "Stacks allow you to push operations and pop them when undoing."},

    {"id": 8, "question": "What is the time complexity of inserting an element in a max heap?", 
     "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"], "answer": "O(log n)", 
     "explanation": "Heap insertion requires percolating up, which takes logarithmic time."},

    {"id": 9, "question": "Which algorithm is NOT a divide-and-conquer algorithm?", 
     "options": ["Merge Sort", "Quick Sort", "Binary Search", "Dijkstra’s Algorithm"], "answer": "Dijkstra’s Algorithm", 
     "explanation": "Dijkstra’s Algorithm is a greedy algorithm, not divide-and-conquer."},

    # Medium Questions
    {"id": 10, "question": "What is the time complexity of Floyd-Warshall’s algorithm for all-pairs shortest path?", 
     "options": ["O(n log n)", "O(n^3)", "O(n^2)", "O(n)"], "answer": "O(n^3)", 
     "explanation": "Floyd-Warshall algorithm runs in O(n^3) as it updates all pairs iteratively."},

    {"id": 11, "question": "Which data structure is best for implementing a LRU (Least Recently Used) Cache?", 
     "options": ["Stack", "Queue", "Doubly Linked List + HashMap", "Heap"], "answer": "Doubly Linked List + HashMap", 
     "explanation": "This combination allows O(1) access and deletion, making it optimal."},

    {"id": 12, "question": "Which of these algorithms is used for cycle detection in a directed graph?", 
     "options": ["Dijkstra’s Algorithm", "Kruskal’s Algorithm", "DFS (Depth-First Search)", "Prim’s Algorithm"], "answer": "DFS (Depth-First Search)", 
     "explanation": "DFS with recursion stack or visited tracking helps detect cycles."},

    # Hard Questions
    {"id": 13, "question": "Which data structure would be best suited for implementing an efficient priority queue?", 
     "options": ["Binary Search Tree", "Heap", "Array", "Linked List"], "answer": "Heap", 
     "explanation": "Heaps allow O(log n) insertions and O(1) retrieval of the max/min element."},

    {"id": 14, "question": "Which algorithm is most efficient for finding the minimum spanning tree of a dense graph?", 
     "options": ["Prim’s Algorithm", "Kruskal’s Algorithm", "Bellman-Ford", "Dijkstra’s Algorithm"], "answer": "Prim’s Algorithm", 
     "explanation": "Prim’s algorithm is more efficient than Kruskal’s for dense graphs."},

    {"id": 15, "question": "Which recurrence relation represents the runtime of the Merge Sort algorithm?", 
     "options": ["T(n) = 2T(n/2) + O(n)", "T(n) = T(n-1) + O(n)", "T(n) = 3T(n/3) + O(n)", "T(n) = T(n/2) + O(1)"], 
     "answer": "T(n) = 2T(n/2) + O(n)", 
     "explanation": "MergeSort divides the array into two parts and merges them, leading to O(n log n) time complexity."}
]

class Game:
    def __init__(self):
        self.state = MAIN_MENU
        self.score = 0
        self.max_score = len(questions) * 10
        self.question_pool = questions.copy()
        random.shuffle(self.question_pool)
        self.current_question = None
        self.next_question()

    def next_question(self):
        """ Get the next random question without repeating until all are used. """
        if not self.question_pool:
            self.question_pool = questions.copy()
            random.shuffle(self.question_pool)
        self.current_question = self.question_pool.pop(0)  

    def check_answer(self, selected_option):
        """ Check if answer is correct, update score, and move to next question. """
        if self.current_question["options"][selected_option] == self.current_question["answer"]:
            self.score += 10
            if correct_sound: correct_sound.play()
        else:
            if wrong_sound: wrong_sound.play()
        self.next_question()

    def render_quiz(self):
        """ Display the current quiz question and answers. """
        screen.fill(WHITE)
        question = self.current_question
        draw_text(f"Score: {self.score}", font, WIDTH // 2, 50, BLUE)
        draw_text(question["question"], font, WIDTH // 2, 100, BLACK)

        y_offset = 200
        for i, option in enumerate(question["options"]):
            if draw_button(option, WIDTH // 2 - 150, y_offset + i * 60, 300, 50, GRAY, GREEN):
                self.check_answer(i)

    def render_results(self):
        """ Display quiz results. """
        screen.fill(DARK_BLUE)
        draw_text("Quiz Complete!", title_font, WIDTH // 2, 100, WHITE)
        draw_text(f"Final Score: {self.score}", font, WIDTH // 2, 200, GREEN)

        if draw_button("Play Again", WIDTH // 2 - 100, 300, 200, 50, GRAY, GREEN):
            self.__init__()

    def run(self):
        """ Main game loop. """
        running = True
        clock = pygame.time.Clock()
        while running:
            screen.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Optional: Add key controls here if needed
                    pass
                    
            # Render based on current game state
            if self.state == MAIN_MENU:
                # Add rendering for main menu
                draw_text("DSA Quiz: Become the King! \U0001F451", title_font, WIDTH // 2, 100, BLUE)
                draw_text("Test your Data Structures & Algorithms knowledge", font, WIDTH // 2, 180, BLACK)
                
                if draw_button("Start Quiz", WIDTH // 2 - 100, 250, 200, 50, GRAY, GREEN):
                    self.state = QUIZ
                    
                if draw_button("Quit", WIDTH // 2 - 100, 330, 200, 50, GRAY, RED):
                    running = False
            elif self.state == QUIZ:
                self.render_quiz()
            elif self.state == RESULTS:
                self.render_results()
            
            # Update display
            pygame.display.flip()
            clock.tick(60)  # Limit to 60 FPS
        
        pygame.quit()
        sys.exit()
# Utility functions
def draw_text(text, font, x, y, color=BLACK):
    """ Draw text centered at (x, y). """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_button(text, x, y, width, height, color, hover_color):
    """ Draw a button and return True if clicked. """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, hover_color if x < mouse[0] < x + width and y < mouse[1] < y + height else color, (x, y, width, height))
    draw_text(text, font, x + width // 2, y + height // 2, BLACK)
    return click[0] == 1 and x < mouse[0] < x + width and y < mouse[1] < y + height

game = Game()
game.run()

