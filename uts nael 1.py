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
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(-self.angle, 0, 0, 1)

        # Badan mobil (tampilan dari atas)
        glBegin(GL_QUADS)
        glColor3f(*self.color)
        glVertex2f(-0.08, 0.15)  # Depan kiri
        glVertex2f(0.08, 0.15)   # Depan kanan
        glVertex2f(0.08, -0.15)  # Belakang kanan
        glVertex2f(-0.08, -0.15) # Belakang kiri
        glEnd()

        # Kaca depan (tampilan dari atas)
        glBegin(GL_QUADS)
        glColor3f(0.7, 0.7, 0.7)
        glVertex2f(-0.06, 0.05)
        glVertex2f(0.06, 0.05)
        glVertex2f(0.06, -0.05)
        glVertex2f(-0.06, -0.05)
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
        half_width = 0.08
        half_height = 0.15
        corners = [
            (-half_width, half_height),  # Depan kiri
            (half_width, half_height),   # Depan kanan
            (half_width, -half_height),  # Belakang kanan
            (-half_width, -half_height)  # Belakang kiri
        ]
        
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
        
        # Dapatkan koordinat 4 sudut mobil
        car_corners = car.get_corners()
        
        for spot_idx, (spot_x, spot_y, spot_width, spot_height) in enumerate(parking_spots):
            # Cek apakah semua sudut mobil ada di dalam area parkir
            corners_inside = 0
            any_corner_touching_border = False
            
            for corner_x, corner_y in car_corners:
                # Periksa apakah sudut ada di dalam area parkir
                if (spot_x < corner_x < spot_x + spot_width and 
                    spot_y - spot_height < corner_y < spot_y):
                    corners_inside += 1
                
                # Cek apakah sudut menyentuh atau terlalu dekat dengan batas
                border_margin = 0.015  # Margin untuk deteksi menyentuh border
                if (((spot_x <= corner_x <= spot_x + border_margin) or 
                     (spot_x + spot_width - border_margin <= corner_x <= spot_x + spot_width)) and
                    spot_y - spot_height < corner_y < spot_y):
                    any_corner_touching_border = True
                
                if (((spot_y - spot_height <= corner_y <= spot_y - spot_height + border_margin) or 
                     (spot_y - border_margin <= corner_y <= spot_y)) and
                    spot_x < corner_x < spot_x + spot_width):
                    any_corner_touching_border = True
            
            # Setel status parkir berdasarkan posisi mobil
            if corners_inside == 4:  # Semua sudut di dalam
                if any_corner_touching_border:
                    parking_statuses[spot_idx] = 2  # Parkir menyentuh garis (oranye)
                else:
                    parking_statuses[spot_idx] = 1  # Parkir sempurna (hijau)
                
                occupied_spots.append(spot_idx)
                car.parked = True
                car.spot_index = spot_idx
                
                if parking_statuses[spot_idx] == 1:
                    success_timer = 60  # Teks parkir berhasil

def draw_parking_lot():
    for i, (x, y, width, height) in enumerate(parking_spots):
        # Warna area parkir berdasarkan status
        if i in occupied_spots:
            status = parking_statuses[i]
            if status == 1:  # Parkir sempurna
                glColor3f(0.0, 0.6, 0.0)  # Hijau 
            elif status == 2:  # Parkir menyentuh garis
                glColor3f(1.0, 0.0, 0.0)  # Merah
        else:
            glColor3f(1.0, 1.0, 0.0)  # Kuning untuk slot yang tersedia
        
        # Gambar area parkir
        glBegin(GL_QUADS)
        glVertex2f(x + 0.01, y - 0.01)
        glVertex2f(x + width - 0.01, y - 0.01)
        glVertex2f(x + width - 0.01, y - height + 0.01)
        glVertex2f(x + 0.01, y - height + 0.01)
        glEnd()
        
        # Garis pembatas parkir
        glColor3f(1.0, 1.0, 1.0)  # Warna putih untuk garis
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
        font = pygame.font.Font(None, 48)
        success_text = font.render('Parkir Berhasil!', True, (0, 255, 0))
        text_surface = pygame.Surface((300, 50), pygame.SRCALPHA)
        text_surface.blit(success_text, (0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glWindowPos2f(250, 550)  # Posisi tengah atas layar
        glDrawPixels(300, 50, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

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
