import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview

from main import *
cnx = mysql.connector.connect(**{'user':'root','password':'tinytin03@21','host':'localhost','db':'Library'})
todays_date = datetime.today()

class PayFines:
    def __init__(self, master):
        self.parent = master

        self.v = StringVar()

        self.borrowerLabel = Label(self.parent, text="Borrower ID ").grid(row=0, column=0, padx=20, pady=20)
        self.borrowerEntry = Entry(self.parent)
        self.borrowerEntry.grid(row=1, column=0, padx=20, pady=20)
        self.showFineBtn = Button(self.parent, text="Show Fines", command=self.show_fines).grid(row=2, column=0, padx=20, pady=20)
        self.fineLabel = Label(self.parent, textvariable=self.v)
        self.fineLabel.grid(row=3, column=0, padx=20, pady=20)
        self.payFineBtn = Button(self.parent, text="Pay Fine", command=self.pay_fine).grid(row=4, column=0, padx=20, pady=20)

    def show_fines(self):
        borrower_id = self.borrowerEntry.get()
        cursor = cnx.cursor()
        cursor.execute("SELECT EXISTS(SELECT Card_ID FROM borrower WHERE borrower.Card_ID = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        total_fine = 0

        if result == [(0,)]:
            messagebox.showinfo("Error", "Enter Valid Borrower")
        else:
            cursor.execute("SELECT fines.Fine_Amt, fines.Paid FROM fines JOIN book_loans ON fines.LoanID = book_loans.LoanID WHERE book_loans.Card_ID = '" + str(borrower_id) + "'")
            result = cursor.fetchall()
            total_fine = 0
            for elem in result:
                if elem[1] == 0:
                    total_fine += float(elem[0])

        self.v.set("Fine: $ " + str(total_fine))

    def pay_fine(self):
        borrower_id = self.borrowerEntry.get()
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT Card_ID FROM borrower WHERE borrower.Card_ID = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower does not exist in data")
        else:
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT fines.LoanID FROM fines JOIN book_loans ON fines.LoanID = book_loans.LoanID WHERE book_loans.Card_ID = '" + str(
                    borrower_id) + "'")
            result = cursor.fetchall()
            for elem in result:
                cursor = cnx.cursor()
                cursor.execute("UPDATE fines SET fines.Paid = 1 WHERE fines.LoanID = '" + str(elem[0]) + "'")
                cnx.commit()
            messagebox.showinfo("Info", "Fines Paid!")
            self.parent.destroy()
