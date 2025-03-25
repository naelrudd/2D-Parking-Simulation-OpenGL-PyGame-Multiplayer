import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from math import cos, sin, radians, degrees, sqrt
import random
import numpy as np

# Konstanta warna
COLORS = {
    'WHITE': (1.0, 1.0, 1.0),
    'BLACK': (0.0, 0.0, 0.0),
    'RED': (1.0, 0.0, 0.0),
    'GREEN': (0.0, 1.0, 0.0),
    'BLUE': (0.0, 0.0, 1.0),
    'YELLOW': (1.0, 1.0, 0.0),
    'CYAN': (0.7, 1.0, 1.0),
    'GRAY': (0.5, 0.5, 0.5),
    'DARK_GRAY': (0.3, 0.3, 0.3),
    'ORANGE': (0.8, 0.4, 0.0)
}

# Layout parkir 2 kolom 4 baris
parking_spots = [
    # Kolom 1 (kiri)
    (-0.75, 0.8, 0.5, 0.35),   # Baris 1
    (-0.75, 0.4, 0.5, 0.35),   # Baris 2
    (-0.75, 0.0, 0.5, 0.35),   # Baris 3
    (-0.75, -0.4, 0.5, 0.35),  # Baris 4
    
    # Kolom 2 (kanan)
    (0.25, 0.8, 0.5, 0.35),    # Baris 1
    (0.25, 0.4, 0.5, 0.35),    # Baris 2
    (0.25, 0.0, 0.5, 0.35),    # Baris 3
    (0.25, -0.4, 0.5, 0.35),   # Baris 4
]

# Status parkir dan pemain
occupied_spots = []
parking_statuses = []  # 0: kosong, 1: parkir sempurna, 2: parkir menyentuh garis
success_timer = 0

# Class untuk mobil
class Car:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.angle = 0
        self.steering_angle = 0
        self.current_speed = 0.0
        self.color = color
        self.controls = controls  # Dictionary dengan kontrol tombol
        self.parked = False
        self.spot_index = -1
    
    # Layout parkir 2 kolom 4 baris - made slightly smaller
    parking_spots = [
        # Kolom 1 (kiri)
        (-0.65, 0.7, 0.4, 0.3),   # Baris 1
        (-0.65, 0.35, 0.4, 0.3),   # Baris 2
        (-0.65, 0.0, 0.4, 0.3),   # Baris 3
        (-0.65, -0.35, 0.4, 0.3),  # Baris 4
        
        # Kolom 2 (kanan)
        (0.25, 0.7, 0.4, 0.3),    # Baris 1
        (0.25, 0.35, 0.4, 0.3),    # Baris 2
        (0.25, 0.0, 0.4, 0.3),    # Baris 3
        (0.25, -0.35, 0.4, 0.3),   # Baris 4
    ]
    
    # In Car class, update the car size
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(-self.angle, 0, 0, 1)
    
        # Badan mobil - made longer
        glBegin(GL_QUADS)
        glColor3f(*self.color)
        glVertex2f(-0.09, 0.17) 
        glVertex2f(0.09, 0.17)   
        glVertex2f(0.09, -0.17)  
        glVertex2f(-0.09, -0.17) 
        glEnd()
    
        # Kaca depan - adjusted for longer body
        glBegin(GL_QUADS)
        glColor3f(0.7, 0.7, 0.7)
        glVertex2f(-0.07, 0.08)  # Increased width from 0.06 to 0.07
        glVertex2f(0.07, 0.08)
        glVertex2f(0.07, -0.08)
        glVertex2f(-0.07, -0.08)
        glEnd()
    
        glPopMatrix()
    
    def update(self, keys, dt):
        # Parameter kecepatan dan kemudi
        max_speed = 0.008  # Lebih lambat
        min_speed_for_turn = 0.002
        acceleration = 0.0003
        deceleration = 0.0002
        max_steering_angle = 12
        steering_speed = 0.6
        turning_factor = 0.2
        
        # Akselerasi dan deselerasi
        if keys[self.controls['up']]:
            self.current_speed = min(self.current_speed + acceleration, max_speed)
        elif keys[self.controls['down']]:
            self.current_speed = max(self.current_speed - acceleration, -max_speed)
        else:
            # Perlambatan alami
            if abs(self.current_speed) < deceleration:
                self.current_speed = 0
            elif self.current_speed > 0:
                self.current_speed -= deceleration
            elif self.current_speed < 0:
                self.current_speed += deceleration
        
        # Debugging: Print kecepatan
        print(f"Kecepatan: {self.current_speed}")
        
        # Kontrol kemudi
        if keys[self.controls['left']]:
            self.steering_angle = max(self.steering_angle - steering_speed, -max_steering_angle)
        elif keys[self.controls['right']]:
            self.steering_angle = min(self.steering_angle + steering_speed, max_steering_angle)
        else:
            # Kemudi kembali ke posisi tengah secara perlahan
            if abs(self.steering_angle) < steering_speed:
                self.steering_angle = 0
            elif self.steering_angle > 0:
                self.steering_angle -= steering_speed
            else:
                self.steering_angle += steering_speed
        
        # Update posisi dan rotasi mobil
        if self.current_speed != 0:
            # Hanya berbelok jika kecepatan cukup
            turn_multiplier = 0
            if abs(self.current_speed) > min_speed_for_turn:
                # Faktor belok berdasarkan kecepatan
                speed_factor = min((abs(self.current_speed) - min_speed_for_turn) / (max_speed - min_speed_for_turn), 1.0)
                turn_multiplier = speed_factor * turning_factor
            
            # Update sudut mobil berdasarkan kemudi dan kecepatan
            self.angle += self.steering_angle * turn_multiplier
            
            # Update posisi
            new_x = self.x + self.current_speed * sin(radians(self.angle))
            new_y = self.y + self.current_speed * cos(radians(self.angle))
            
            # Batas window
            if -1 + 0.08 < new_x < 1 - 0.08:
                self.x = new_x
            if -1 + 0.15 < new_y < 1 - 0.15:
                self.y = new_y
    
    def get_corners(self):
        # Mendapatkan koordinat 4 sudut mobil berdasarkan posisi dan sudut
        half_width = 0.09
        half_height = 0.18
        
        # Add more sensor points for better detection
        side_sensor_points = [
            (-half_width, half_height*0.9),    # Kiri depan atas
            (-half_width, half_height*0.6),    # Kiri depan tengah
            (-half_width, half_height*0.3),    # Kiri depan bawah
            (-half_width, 0),                  # Kiri tengah
            (-half_width, -half_height*0.3),   # Kiri belakang atas
            (-half_width, -half_height*0.6),   # Kiri belakang tengah
            (-half_width, -half_height*0.9),   # Kiri belakang bawah
            
            (half_width, half_height*0.9),     # Kanan depan atas
            (half_width, half_height*0.6),     # Kanan depan tengah
            (half_width, half_height*0.3),     # Kanan depan bawah
            (half_width, 0),                   # Kanan tengah
            (half_width, -half_height*0.3),    # Kanan belakang atas
            (half_width, -half_height*0.6),    # Kanan belakang tengah
            (half_width, -half_height*0.9),    # Kanan belakang bawah
            
            (0, half_height),                  # Tengah depan
            (0, -half_height),                 # Tengah belakang
        ]
        
        corners = [
            (-half_width, half_height),    # Depan kiri
            (half_width, half_height),     # Depan kanan
            (half_width, -half_height),    # Belakang kanan
            (-half_width, -half_height),   # Belakang kiri
        ] + side_sensor_points

        # Transformasi sudut sesuai rotasi mobil
        rotated_corners = []
        for x, y in corners:
            angle_rad = radians(self.angle)
            rotated_x = x * cos(angle_rad) - y * sin(angle_rad)
            rotated_y = x * sin(angle_rad) + y * cos(angle_rad)
            rotated_corners.append((self.x + rotated_x, self.y + rotated_y))
        
        return rotated_corners

def draw_background():
    # Gambar latar belakang parkiran (aspal)
    glColor3f(0.2, 0.2, 0.2)  # Warna aspal
    glBegin(GL_QUADS)
    glVertex2f(-1, 1)
    glVertex2f(1, 1)
    glVertex2f(1, -1)
    glVertex2f(-1, -1)
    glEnd()

def draw_parking_lines():
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    for x, y, width, height in parking_spots:
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y - height)
        glVertex2f(x, y - height)
        glEnd()

def check_parking_status(cars):
    global parking_statuses, occupied_spots, success_timer
    
    # Reset status parkir
    parking_statuses = [0] * len(parking_spots)  # 0: kosong
    occupied_spots = []
    
    for car_idx, car in enumerate(cars):
        car.parked = False
        car.spot_index = -1
        
        # Dapatkan koordinat sudut mobil dan sensor
        car_points = car.get_corners()
        car_corners = car_points[:4]  # 4 sudut utama
        
        for spot_idx, (spot_x, spot_y, spot_width, spot_height) in enumerate(parking_spots):
            corners_inside = 0
            any_point_touching_border = False
            
            # Check if any point is near or inside the spot
            for point_x, point_y in car_points:
                # Increased margin for better border detection
                margin = 0.015  # Smaller margin for more precise detection
                
                # First check if point is in the general area of the spot
                if (spot_x - margin <= point_x <= spot_x + spot_width + margin and
                    spot_y - spot_height - margin <= point_y <= spot_y + margin):
                    
                    # More precise border detection
                    if (abs(point_x - spot_x) <= margin or  # Left border
                        abs(point_x - (spot_x + spot_width)) <= margin or  # Right border
                        abs(point_y - spot_y) <= margin or  # Top border
                        abs(point_y - (spot_y - spot_height)) <= margin):  # Bottom border
                        
                        any_point_touching_border = True
                        parking_statuses[spot_idx] = 2  # Touching lines
                        occupied_spots.append(spot_idx)
                        car.parked = True
                        car.spot_index = spot_idx
                        break
            
            # Check for perfect parking only with main corners
            if not any_point_touching_border:
                corners_inside = sum(1 for x, y in car_corners 
                                  if (spot_x + margin < x < spot_x + spot_width - margin and 
                                      spot_y - spot_height + margin < y < spot_y - margin))
                
                if corners_inside == 4:
                    parking_statuses[spot_idx] = 1  # Perfect parking
                    occupied_spots.append(spot_idx)
                    car.parked = True
                    car.spot_index = spot_idx
                    success_timer = 60

def draw_parking_lot():
    for i, (x, y, width, height) in enumerate(parking_spots):
        # Warna area parkir berdasarkan status
        if i in occupied_spots:
            status = parking_statuses[i]
            if status == 1:  # Parkir sempurna
                glColor3f(0.0, 0.6, 0.0)  # Hijau 
            elif status == 2:  # Parkir menyentuh garis
                glColor3f(1.0, 0.8, 0.0)  # Kuning untuk menyentuh garis
            else:
                glColor3f(0.25, 0.25, 0.25)  # Abu-abu untuk slot kosong
        else:
            glColor3f(0.25, 0.25, 0.25)  # Abu-abu untuk slot kosong
        
        # Gambar area parkir
        glBegin(GL_QUADS)
        glVertex2f(x + 0.01, y - 0.01)
        glVertex2f(x + width - 0.01, y - 0.01)
        glVertex2f(x + width - 0.01, y - height + 0.01)
        glVertex2f(x + 0.01, y - height + 0.01)
        glEnd()
        
        # Garis pembatas parkir
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y - height)
        glVertex2f(x, y - height)
        glEnd()
        
        # Perbaikan tampilan nomor slot
        font = pygame.font.Font(None, 36)  # Ukuran font lebih besar
        slot_text = font.render(str(i + 1), True, (0, 0, 0))  # Warna hitam
        text_surface = pygame.Surface((30, 30), pygame.SRCALPHA)  # Surface lebih besar
        text_surface.fill((255, 255, 255, 128))  # Background putih semi-transparan
        text_rect = slot_text.get_rect(center=(15, 15))  # Posisi tengah
        text_surface.blit(slot_text, text_rect)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Posisi teks yang lebih tepat
        screen_x = int((x + width/2) * 400 + 400 - 15)
        screen_y = int((y - height/2) * 300 + 300 - 15)
        glWindowPos2f(screen_x, screen_y)
        glDrawPixels(30, 30, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_success_message():
    if success_timer > 0:
        # Count perfectly parked cars
        perfect_parks = sum(1 for status in parking_statuses if status == 1)
        
        font = pygame.font.Font(None, 48)
        success_text = font.render(f'Parkir Berhasil! {perfect_parks}/2', True, (50, 50, 0))  # Dark yellow text
        text_surface = pygame.Surface((400, 60), pygame.SRCALPHA)  # Increased width from 300 to 400
        
        # Lighter background
        background = pygame.Surface((400, 60))  # Increased width to match surface
        background.fill((255, 255, 150))  # Light yellow background
        background.set_alpha(180)  # More opaque background
        text_surface.blit(background, (0, 0))
        
        # Center the text on the wider surface
        text_rect = success_text.get_rect(center=(200, 30))  # Adjusted center x from 150 to 200
        text_surface.blit(success_text, text_rect)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Position in center top of screen, adjusted for wider surface
        glWindowPos2f(200, 520)  # Adjusted x position from 250 to 200 to maintain center
        glDrawPixels(400, 60, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_scene(cars):
    global success_timer
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_background()
    check_parking_status(cars)
    draw_parking_lot()
    
    # Gambar semua mobil
    for car in cars:
        car.draw()
        
    draw_success_message()
    
    if success_timer > 0:
        success_timer -= 1
    
    pygame.display.flip()

def draw_player_info():
    font = pygame.font.Font(None, 30)
    
    # Info pemain 1
    p1_text = font.render('Pemain 1: WASD', True, (255, 255, 255))
    p1_surface = pygame.Surface((200, 30), pygame.SRCALPHA)
    p1_surface.blit(p1_text, (0, 0))
    p1_data = pygame.image.tostring(p1_surface, "RGBA", True)
    
    glWindowPos2f(10, 570)
    glDrawPixels(200, 30, GL_RGBA, GL_UNSIGNED_BYTE, p1_data)
    
    # Info pemain 2
    p2_text = font.render('Pemain 2: Arrow Keys', True, (255, 255, 255))
    p2_surface = pygame.Surface((200, 30), pygame.SRCALPHA)
    p2_surface.blit(p2_text, (0, 0))
    p2_data = pygame.image.tostring(p2_surface, "RGBA", True)
    
    glWindowPos2f(590, 570)
    glDrawPixels(200, 30, GL_RGBA, GL_UNSIGNED_BYTE, p2_data)

def update_car_position(car, dt):
    # Menggunakan numpy untuk perhitungan vektor
    direction = np.array([sin(radians(car.angle)), cos(radians(car.angle))])
    new_position = np.array([car.x, car.y]) + car.current_speed * direction * dt
    
    # Batas window
    if -1 + 0.08 < new_position[0] < 1 - 0.08:
        car.x = new_position[0]
    if -1 + 0.15 < new_position[1] < 1 - 0.15:
        car.y = new_position[1]

def draw_status_text():
    font = pygame.font.Font(None, 30)
    status_text = "Status Parkir: "
    for i, status in enumerate(parking_statuses):
        if status == 0:
            status_text += f"Slot {i+1}: Kosong  "
        elif status == 1:
            status_text += f"Slot {i+1}: Sempurna  "
        elif status == 2:
            status_text += f"Slot {i+1}: Menyentuh  "
    
    text_surface = font.render(status_text, True, (255, 255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2f(10, 10)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("Simulasi Parkir Mobil - 2 Pemain")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    
    # Inisialisasi 2 mobil pemain
    car1 = Car(
        x=-0.5, 
        y=-0.85, 
        color=COLORS['RED'], 
        controls={
            'up': K_w, 
            'down': K_s, 
            'left': K_a, 
            'right': K_d
        }
    )
    
    car2 = Car(
        x=0.5, 
        y=-0.85, 
        color=COLORS['BLUE'], 
        controls={
            'up': K_UP, 
            'down': K_DOWN, 
            'left': K_LEFT, 
            'right': K_RIGHT
        }
    )
    
    cars = [car1, car2]
    
    keys = {}
    for key in [K_w, K_s, K_a, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT]:
        keys[key] = False
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == KEYDOWN:
                if event.key in keys:
                    keys[event.key] = True
            elif event.type == KEYUP:
                if event.key in keys:
                    keys[event.key] = False
        
        # Update mobil
        dt = clock.tick(60) / 1000.0  # Delta time dalam detik
        for car in cars:
            car.update(keys, dt)
            update_car_position(car, dt)
        
        # Gambar scene
        draw_scene(cars)
        
        # Tampilkan info pemain
        draw_player_info()
    
    pygame.quit()

if __name__ == "__main__":
    main()
