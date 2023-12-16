"""
This animation is rendered by manim
You can download manim in https://github.com/3b1b/manim
"""

from manimlib import *
import numpy as np

NUM_FIREFLIES = 20
FIRING_SPAN = 25
RESTING_SPAN = 75
WEIGHT = 0.7
NUMBERS = 100
K = 5
MAX_NUM_LOOPING = 20
ANIMATION_SPEED = 50


class Fireflies:

    def __init__(self, num_fireflies, rectangle_size=(1, 1), positions=None):
        """
        A class to store all the fireflies.
        """
        self.size = np.array(rectangle_size)
        self.num_fireflies = num_fireflies
        self.k = K
        self.max = 0
        # Initial the spans
        init_spans = np.random.rand(num_fireflies) * (FIRING_SPAN + RESTING_SPAN)
        # decide which is fired and which is extinguished.
        self.statuses = (init_spans < FIRING_SPAN)
        # Initial the first lasting span
        self.next_event_spans = \
            np.array(list(map(lambda t: t if t < FIRING_SPAN else t - FIRING_SPAN, init_spans)))
        # positions of the fireflies.
        self.positions = positions or np.random.rand(num_fireflies, 2) * np.array(rectangle_size)
        # adjacency matrix storing all the neighbors.
        self.adjacency = np.zeros((num_fireflies, num_fireflies), dtype=np.int8)
        for i in range(num_fireflies - 1):
            position = self.positions[i]
            # Sort all the nodes by distance.
            neighbors_by_dis = np.argsort([np.linalg.norm(position - self.positions[j]) 
            for j in range(num_fireflies)])
            # Pick out the k-nearest nodes.
            kneighbors = neighbors_by_dis[1:self.k+1]
            # Update the adjacency matrix
            self.adjacency[i, kneighbors] = 1
    
    def get_k_neighbors(self, firefly_id):
        """
        Pick out the k-nearest neighbors according to the adjacency matrix.
        """
        return [i for i, label in enumerate(self.adjacency[firefly_id]) if label == 1]
    
    def change(self, firefly_id):
        """
        Changes the status of a firefly, and affecting others.
        """
        if self.statuses[firefly_id]:
            # If it is firing, turns into resting.
            self.statuses[firefly_id] = 0
            self.next_event_spans[firefly_id] = RESTING_SPAN
            # Search for k_neighbors. If lighting, diminish its own resting span.
            for neighbor_id in self.get_k_neighbors(firefly_id):
                if self.statuses[neighbor_id]:
                    self.next_event_spans[firefly_id] *= WEIGHT
        else:
            # If it is resting, turns into firing.
            self.statuses[firefly_id] = 1
            self.next_event_spans[firefly_id] = FIRING_SPAN
            # Search for k_neighbors. If resting, diminish their resting spans.
            for neighbor_id in self.get_k_neighbors(firefly_id):
                if not self.statuses[neighbor_id]:
                    self.next_event_spans[neighbor_id] *= WEIGHT
    
    def get_position_3d(self, firefly_id):
        """
        In manim, positions should be described in 3-D vectors.
        """
        return np.concatenate([self.positions[firefly_id], [0]])

    def start_simulation(self):
        for _ in range(MAX_NUM_LOOPING * self.num_fireflies):
            # Find the next event:
            next_firefly = np.argmin(self.next_event_spans)
            time_span = self.next_event_spans[next_firefly]
            yield next_firefly, time_span, self.statuses[next_firefly]
            self.next_event_spans -= time_span
            self.change(next_firefly)
            self.max = max(np.sum(self.statuses), self.max)


class FirefliesAnimation(Scene):

    def setup(self):
        np.random.seed(100)
        self.colors = [GREY, YELLOW]
        self.add(Rectangle(12.4, 7.4))
        fireflies = Fireflies(NUM_FIREFLIES, rectangle_size=(12, 7))
        self.fireflies = fireflies
        self.firefly_points = VGroup(*[
            Dot().set_color(YELLOW).shift(
                self.fireflies.get_position_3d(i)
            ).shift(np.array([-6, -3.5, 0]))
            if self.fireflies.statuses[i] # If the firefly is firing
            else Dot().set_color(GREY).shift(
                self.fireflies.get_position_3d(i)
            ).shift(np.array([-6, -3.5, 0]))
            for i in range(NUM_FIREFLIES)
        ])
        # self.bloods = VGroup(*[
        #     Rectangle(0.5, 0.05, stroke_width=0, fill_color=BLUE, fill_opacity=0.5)\
        #         .move_to(dot.get_center() + 0.2 * UP)
        #     for dot in self.firefly_points
        # ])
        # self.blood_frames = VGroup(*[
        #     Rectangle(0.5, 0.05, stroke_width=0.03)\
        #         .move_to(dot.get_center() + 0.2 * UP)
        #     for dot in self.firefly_points
        # ])
        self.add(self.firefly_points)
        # self.next_event_spans = fireflies.next_event_spans
        self.total_time = 0
        # self.total_time_text = Text('Total time: ').next_to(TOP + LEFT_SIDE, direction=DR)
        self.max_num_text = Text('Max:').next_to(TOP + LEFT_SIDE, direction=DR)
        self.current_firing_text = Text('Current:').next_to(self.max_num_text, DOWN)
        self.add(
            # self.total_time_text, 
        self.max_num_text, self.current_firing_text)

        # self.total_time_num = DecimalNumber().next_to(self.total_time_text)
        # self.total_time_num.add_updater(lambda obj: \
        #     obj.set_value(self.total_time)
        # )
        self.max_num = DecimalNumber().next_to(self.max_num_text)
        self.max_num.add_updater(lambda obj: \
            obj.set_value(self.fireflies.max)
        )
        self.current_firing_num = DecimalNumber().next_to(self.current_firing_text)
        self.current_firing_num.add_updater(lambda obj:\
            obj.set_value(np.sum(self.fireflies.statuses))
        )
        self.add(
            # self.total_time_num, 
            self.max_num, self.current_firing_num)

    
    # Change the simulation into time
    def construct(self):
        frame = self.camera.frame
        fireflies = self.fireflies
        # def blood_update_func(obj: Mobject):
        #     if fireflies.statuses[index]:
        #         blood_value = 0.5 * self.next_event_spans[index] / FIRING_SPAN
        #         color = RED
        #     else:
        #         blood_value = 0.5 * self.next_event_spans[index] / RESTING_SPAN
        #         color = BLUE
        #     obj.set_width(0.5 * blood_value, stretch=True).set_color(color)\
        #         .next_to(self.blood_frames[index].get_left(), direction=RIGHT, buff=0)
        # for index, blood in enumerate(self.bloods):
        #     blood.add_updater(blood_update_func)
        for firefly, time_span, status in fireflies.start_simulation():
            # self.next_event_spans = next_event_spans
            # coordinate = self.fireflies.get_position_3d(firefly)
            self.total_time += time_span
            if status:
                # From firing to resting
                self.play(CircleIndicate(self.firefly_points[firefly], color=GREY),
                    *[Flash(
                        self.firefly_points[i], color=RED
                    ) for i in fireflies.get_k_neighbors(firefly_id=firefly)
                    if fireflies.statuses[i] == 1
                    ],
                    Transform(self.firefly_points[firefly], self.firefly_points[firefly].set_color(
                        GREY
                    )), run_time=0.3
                )
            else:
                # From resting to firing
                self.play(Flash(self.firefly_points[firefly]),
                    *[CircleIndicate(
                        self.firefly_points[i], color=GREY
                    ) for i in fireflies.get_k_neighbors(firefly_id=firefly)
                    if fireflies.statuses[i] == 0
                    ],
                    Transform(self.firefly_points[firefly], self.firefly_points[firefly].set_color(
                        YELLOW
                    )), run_time=0.3
                )
        
        
