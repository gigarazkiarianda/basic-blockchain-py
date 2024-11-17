import hashlib
import json
import mysql.connector
from datetime import datetime

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="blockchain_db",
        port=3307
    )

class Block:
    def __init__(self, block_index, timestamp, transactions, previous_hash):
        self.block_index = block_index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.block_index}{self.timestamp}{json.dumps(self.transactions)}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_genesis_block()
        self.load_blocks_from_db()

    def create_genesis_block(self):
        if not self.chain:
            genesis_block = Block(0, str(datetime.now()), [], "0")
            self.chain.append(genesis_block)
            self.store_block_in_db(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.current_transactions.append(transaction)

    def edit_transaction(self, index, new_transaction):
        if 0 <= index < len(self.current_transactions):
            self.current_transactions[index] = new_transaction
        else:
            print("Transaksi tidak ditemukan!")

    def delete_transaction(self, index):
        if 0 <= index < len(self.current_transactions):
            del self.current_transactions[index]
        else:
            print("Transaksi tidak ditemukan!")

    def mine_block(self):
        last_block = self.get_last_block()
        new_block = Block(len(self.chain), str(datetime.now()), self.current_transactions, last_block.hash)
        self.chain.append(new_block)
        self.store_block_in_db(new_block)
        self.current_transactions = []

    def store_block_in_db(self, block):
        conn = create_connection()
        cursor = conn.cursor()
        query = "INSERT INTO blocks (block_index, timestamp, previous_hash, hash, transactions) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (block.block_index, block.timestamp, block.previous_hash, block.hash, json.dumps(block.transactions)))
        conn.commit()
        cursor.close()
        conn.close()

    def load_blocks_from_db(self):
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM blocks ORDER BY block_index"
        cursor.execute(query)
        blocks = cursor.fetchall()
        for block in blocks:
            block_index = block[0]
            timestamp = block[1]
            previous_hash = block[2]
            hash = block[3]
            transactions_data = block[4]
            try:
                transactions = json.loads(transactions_data)
            except json.JSONDecodeError:
                print(f"Warning: Gagal memparsing transaksi untuk blok index {block_index}. Memuat sebagai transaksi kosong.")
                transactions = []
            block_obj = Block(block_index, timestamp, transactions, previous_hash)
            self.chain.append(block_obj)
        cursor.close()
        conn.close()

    def delete_block(self, block_index):
        if block_index < len(self.chain):
            self.chain = [block for block in self.chain if block.block_index != block_index]
            conn = create_connection()
            cursor = conn.cursor()
            query = "DELETE FROM blocks WHERE block_index = %s"
            cursor.execute(query, (block_index,))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Blok dengan index {block_index} telah dihapus!")
        else:
            print("Blok tidak ditemukan!")

    def display_chain(self):
        for block in self.chain:
            print(f"Index: {block.block_index}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print(f"Transactions: {block.transactions}")
            print("-" * 50)

def display_menu():
    print("\n==== Menu Blockchain ====")
    print("1. Tambah Transaksi")
    print("2. Edit Transaksi")
    print("3. Hapus Transaksi")
    print("4. Tambang Blok")
    print("5. Hapus Blok")
    print("6. Tampilkan Blockchain")
    print("7. Keluar")
    print("==========================")

def start_blockchain():
    blockchain = Blockchain()

    while True:
        display_menu()
        choice = input("Pilih opsi (1-7): ")

        if choice == '1':
            sender = input("Masukkan pengirim: ")
            receiver = input("Masukkan penerima: ")
            amount = float(input("Masukkan jumlah: "))
            blockchain.add_transaction({"sender": sender, "receiver": receiver, "amount": amount})

        elif choice == '2':
            index = int(input("Masukkan index transaksi yang akan diedit: "))
            sender = input("Masukkan pengirim baru: ")
            receiver = input("Masukkan penerima baru: ")
            amount = float(input("Masukkan jumlah baru: "))
            blockchain.edit_transaction(index, {"sender": sender, "receiver": receiver, "amount": amount})

        elif choice == '3':
            index = int(input("Masukkan index transaksi yang akan dihapus: "))
            blockchain.delete_transaction(index)

        elif choice == '4':
            blockchain.mine_block()

        elif choice == '5':
            block_index = int(input("Masukkan index blok yang akan dihapus: "))
            blockchain.delete_block(block_index)

        elif choice == '6':
            blockchain.display_chain()

        elif choice == '7':
            print("Terima kasih! Program selesai.")
            break

        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    start_blockchain()
