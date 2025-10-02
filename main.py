
import psycopg2
from datetime import datetime

# ---------- PostgreSQLga ulanish ----------
def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Marat3107",
        host="localhost",
        port="5432"
    )


# ---------- Jadval yaratish ----------
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        seriyasi VARCHAR(16) PRIMARY KEY,
        pin VARCHAR(4) NOT NULL,
        balans BIGINT NOT NULL,
        karta_turi VARCHAR(20) NOT NULL,
        tarix TEXT[] DEFAULT '{}'::text[]
    )
    """)
    conn.commit()
    conn.close()


# ---------- Asosiy Karta klassi ----------
class Karta:
    def __init__(self, seriyasi, pin, balans, karta_turi, tarix=None):
        self.seriyasi = seriyasi
        self.pin = pin
        self.balans = balans
        self.karta_turi = karta_turi
        self.tarix = list(tarix) if tarix else []

    def balansni_korish(self):
        print(f"{self.karta_turi} ({self.seriyasi}) - Balans: {self.balans:,} so'm")

    def pul_yechish(self, summa):
        if summa <= 0:
            print("Noto‘g‘ri summa.")
            return
        if summa <= self.balans:
            self.balans -= summa
            self.log_qoshish(f"{summa:,} so'm yechildi.")
            print(f"{summa:,} so'm yechildi. Yangi balans: {self.balans:,} so'm")
            self.bazaga_saqlash()
        else:
            print("Balansda mablag‘ yetarli emas.")

    def balansni_toldirish(self, summa):
        if summa > 0:
            self.balans += summa
            self.log_qoshish(f"{summa:,} so'm qo‘shildi.")
            print(f"{summa:,} so'm qo‘shildi. Yangi balans: {self.balans:,} so'm")
            self.bazaga_saqlash()
        else:
            print("Noto‘g‘ri summa.")

    def pinni_ozgartirish(self):
        eski_pin = input("Eski PINni kiriting: ")
        if eski_pin != self.pin:
            print("Noto‘g‘ri PIN.")
            return
        yangi_pin = input("Yangi PIN (4 xonali): ")
        if len(yangi_pin) == 4 and yangi_pin.isdigit():
            self.pin = yangi_pin
            self.log_qoshish("PIN o‘zgartirildi.")
            self.bazaga_saqlash()
            print("PIN muvaffaqiyatli o‘zgartirildi.")
        else:
            print("PIN noto‘g‘ri formatda.")

    def tarixni_korish(self):
        if not self.tarix:
            print("Tarix bo‘sh.")
        else:
            print("----- TRANSAKSIYA TARIXI -----")
            for amal in self.tarix:
                print(amal)

    def log_qoshish(self, amal):
        vaqt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tarix.append(f"[{vaqt}] {amal}")

    def bazaga_saqlash(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE cards
            SET pin = %s, balans = %s, tarix = %s
            WHERE seriyasi = %s
        """, (self.pin, self.balans, self.tarix, self.seriyasi))
        conn.commit()
        conn.close()


class UzCard(Karta):
    def __init__(self, seriya, pin, balans):
        super().__init__(seriya, pin, balans, "UzCard")


class Humo(Karta):
    def __init__(self, seriya, pin, balans):
        super().__init__(seriya, pin, balans, "Humo")


class Visa(Karta):
    def __init__(self, seriya, pin, balans):
        super().__init__(seriya, pin, balans, "Visa")


class MasterCard(Karta):
    def __init__(self, seriya, pin, balans):
        super().__init__(seriya, pin, balans, "MasterCard")


def seed_kartalar():
    kartalar = [
        UzCard("8600123456789012", "1234", 150000),
        Humo("8600987654321098", "4321", 100000),
        Visa("4111111133311111", "1111", 200000),
        MasterCard("5500635200000004", "2222", 300000)
    ]
    conn = get_connection()
    cur = conn.cursor()

    for karta in kartalar:
        cur.execute("SELECT * FROM cards WHERE seriyasi = %s", (karta.seriyasi,))
        if not cur.fetchone():
            karta.log_qoshish("Karta yaratildi.")
            cur.execute("""
                INSERT INTO cards (seriyasi, pin, balans, karta_turi, tarix)
                VALUES (%s, %s, %s, %s, %s)
            """, (karta.seriyasi, karta.pin, karta.balans, karta.karta_turi, karta.tarix))

    conn.commit()
    conn.close()


# ---------- Bankomat Tizimi ----------
class BankomatTizimi:
    def asosiy_menyu(self):
        while True:
            print("\n--- BANKOMAT TIZIMI ---")
            print("1. Tizimga kirish")
            print("2. Yangi karta qo‘shish")
            print("3. Barcha kartalarni ko‘rish")  # yangi qo‘shildi
            print("4. Chiqish")
            tanlov = input("Tanlang (1-4): ")

            if tanlov == "1":
                self.tizimga_kirish()
            elif tanlov == "2":
                self.karta_qoshish()
            elif tanlov == "3":
                self.barcha_kartalarni_korish()
            elif tanlov == "4":
                print("Dasturdan chiqilmoqda...")
                break
            else:
                print("Noto‘g‘ri tanlov.")

    def barcha_kartalarni_korish(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT seriyasi, karta_turi, balans FROM cards")
        kartalar = cur.fetchall()
        conn.close()

        if not kartalar:
            print("Hech qanday karta mavjud emas.")
            return

        print("\n--- Barcha kartalar ro‘yxati ---")
        for karta in kartalar:
            seriya, turi, balans = karta
            print(f"Karta: {seriya} | Turi: {turi} | Balans: {balans:,} so'm")


    def tizimga_kirish(self):
        seriya = input("Karta raqami: ")
        pin = input("PIN kod: ")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT seriyasi, pin, balans, karta_turi, tarix FROM cards WHERE seriyasi = %s", (seriya,))
        row = cur.fetchone()
        conn.close()

        if row and row[1] == pin:
            karta = Karta(row[0], row[1], row[2], row[3], row[4])
            print("Tizimga muvaffaqiyatli kirildi!")

            while True:
                print("\n1. Balansni ko‘rish")
                print("2. Pul yechish")
                print("3. Balansni to‘ldirish")
                print("4. Tarixni ko‘rish")
                print("5. PIN o‘zgartirish")
                print("6. Orqaga")

                tanlov = input("Tanlang (1-6): ")
                if tanlov == "1":
                    karta.balansni_korish()
                elif tanlov == "2":
                    try:
                        summa = int(input("Yechmoqchi bo‘lgan summa: "))
                        karta.pul_yechish(summa)
                    except ValueError:
                        print("Xato summa.")
                elif tanlov == "3":
                    try:
                        summa = int(input("To‘ldiriladigan summa: "))
                        karta.balansni_toldirish(summa)
                    except ValueError:
                        print("Xato summa.")
                elif tanlov == "4":
                    karta.tarixni_korish()
                elif tanlov == "5":
                    karta.pinni_ozgartirish()
                elif tanlov == "6":
                    break
                else:
                    print("Noto‘g‘ri tanlov.")
        else:
            print("Noto‘g‘ri karta yoki PIN.")

    def karta_qoshish(self):
        print("\nYangi karta qo‘shish:")
        seriya = input("Karta raqami (16 xonali): ")
        if not (seriya.isdigit() and len(seriya) == 16):
            print("Karta raqami noto‘g‘ri.")
            return

        pin = input("PIN kod (4 xonali): ")
        if not (pin.isdigit() and len(pin) == 4):
            print("PIN noto‘g‘ri.")
            return

        balans = int(input("Boshlang‘ich balans: "))
        print("1. UzCard  2. Humo  3. Visa  4. MasterCard")
        turi = input("Karta turi tanlang (1-4): ")
        karta_turlari = {"1": "UzCard", "2": "Humo", "3": "Visa", "4": "MasterCard"}
        if turi not in karta_turlari:
            print("Noto‘g‘ri tur tanlandi.")
            return

        karta_turi = karta_turlari[turi]

        if karta_turi == "UzCard":
            yangi_karta = UzCard(seriya, pin, balans)
        elif karta_turi == "Humo":
            yangi_karta = Humo(seriya, pin, balans)
        elif karta_turi == "Visa":
            yangi_karta = Visa(seriya, pin, balans)
        else:
            yangi_karta = MasterCard(seriya, pin, balans)

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM cards WHERE seriyasi = %s", (seriya,))
            if cur.fetchone():
                print("Bu karta raqami allaqachon mavjud.")
                return

            yangi_karta.log_qoshish("Karta yaratildi.")
            cur.execute("""
                INSERT INTO cards (seriyasi, pin, balans, karta_turi, tarix)
                VALUES (%s, %s, %s, %s, %s)
            """, (yangi_karta.seriyasi, yangi_karta.pin, yangi_karta.balans, yangi_karta.karta_turi, yangi_karta.tarix))
            conn.commit()
            print("Yangi karta muvaffaqiyatli qo‘shildi.")
        finally:
            cur.close()
            conn.close()

# ---------- Dastur boshlanishi ----------
if __name__ == "__main__":
    create_table()
    seed_kartalar()
    tizim = BankomatTizimi()
    tizim.asosiy_menyu()

def bazaga_saqlash(self):
    conn = get_connection()
    cur = conn.cursor()

    def format_tarix(tarix_list):
        escaped = [item.replace('"', '\\"') for item in tarix_list]
        return '{' + ','.join(f'"{i}"' for i in escaped) + '}'

    formatted_tarix = format_tarix(self.tarix)

    cur.execute("""
        UPDATE cards
        SET pin = %s, balans = %s, tarix = %s
        WHERE seriyasi = %s
    """, (self.pin, self.balans, formatted_tarix, self.seriyasi))

    conn.commit()
    conn.close()
