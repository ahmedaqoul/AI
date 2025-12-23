# Ahmed AKUL, Ahmed HAMIDI ve ELMUNZİR ELSEYER *Otonom Araç Simülasyonu* yapay zeka projesi
# AI
import pygame

import math

# Pygame'i başlat

pygame.init()

# Renkler

Beyaz = (255, 255, 255)

Siyah = (0, 0, 0)

Kırmızı = (255, 0, 0)

# Ekran boyutları

Genişlik = 800

Yükseklik = 600

ekran = pygame.display.set_mode((Genişlik, Yükseklik))



# Otonom Araba Sınıfı

class Otonom_Araba:

    def __init__(self, başlangıç_x, başlangıç_y):

        self.x = başlangıç_x

        self.y = başlangıç_y

        self. açı = 0

        self.hız = 2

        self.boyut = 20

    def çiz(self):

        # Arabayı dikdörtgen olarak çizin

        pygame.draw.rect(ekran, Kırmızı, [self.x, self.y, self.boyut, self.boyut])



    def hareket_et(self):

        yeni_x = self.x + self.hız * math.sin(math.radians(self.açı))

        yeni_y = self.y - self.hız * math.cos(math.radians(self.açı))



        # Sınır kontrolü

        yeni_x = max(0, min(yeni_x, Genişlik - self.boyut))

        yeni_y = max(0, min(yeni_y, Yükseklik - self.boyut))



        # Çarpışma kontrolü

        if not self.çarpışma_kontrolü(yeni_x, yeni_y):

            self.x = yeni_x

            self.y = yeni_y



    def çarpışma_kontrolü(self, yeni_x, yeni_y):

        for engel in engeller:

            mesafe = math.hypot(engel[0] - yeni_x, engel[1] - yeni_y)

            if mesafe < 30:  # Engel yarıçapı

                return True

        return False



    def sola_dön(self):

        self.açı += 6  # 6 derece sola dön



    def sağa_dön(self):

        self.açı -= 6  # 6 derece sağa dön


    def engellerden_kaçın(self, engel_x, engel_y):

        mesafe = math.hypot(engel_x - self.x, engel_y - self.y)

        if mesafe < 90:  # Engel 90 birimden daha yakınsa

            if engel_x > self.x:

                self.sola_dön()  # Engel sağdaysa sola dön

            else:

                self.sağa_dön()  # Engel soldaysa sağa dön


# Belirli pozisyonlarda engeller oluştur

def engelleri_oluştur():

    return [

        (625, 200),  # Üst sol

        (450, 150),  # Üst sağ

        (300, 200),  # Ortada

        (250, 450),  # Alt sol

        (600, 475)   # Alt sağ

    ]

# Ekranda engelleri çiz

def engelleri_çiz(engeller):

    for engel in engeller:

        pygame.draw.circle(ekran, Siyah, engel, 30)  # Her engeli daire olarak çiz

# Ana döngü

def ana():

    global engeller

    engeller = engelleri_oluştur()  # Sabit engelleri oluştur

    # Arabanın başlangıç pozisyonu

    başlangıç_x, başlangıç_y = Genişlik // 2, Yükseklik - 100

    while any(math.hypot(engel[0] - başlangıç_x, engel[1] - başlangıç_y) < 30 for engel in engeller):

        başlangıç_x += 10  # Eğer çakışıyorsa pozisyonu ayarla

        if başlangıç_x > Genişlik - 50:  # Dışarı çıkarsa sıfırla

            başlangıç_x = 50

    araba = Otonom_Araba(başlangıç_x, başlangıç_y)

    saat = pygame.time.Clock()

    çalışıyor = True

    while çalışıyor:

        ekran.fill(Beyaz)  # Ekranı temizle

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                çalışıyor = False

        # Engelleri çiz

        engelleri_çiz(engeller)

        # Arabanın hareket etmesini sağla ve engellerden kaçın

        for engel in engeller:

            araba.engellerden_kaçın(engel[0], engel[1])

        araba.hareket_et()

        araba.çiz()

        pygame.display.flip()  # Ekranı güncelle
        saat.tick(60)  # Saniyede 60 kare sınırı

    pygame.quit()

if __name__ == "__main__":

    ana()
