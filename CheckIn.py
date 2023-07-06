import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview

from main import *
cnx = mysql.connector.connect(**{'user':'root','password':'tinytin03@21','host':'localhost','db':'Library'})

class CheckIn:
    def __init__(self, master):
        self.parent = master

        self.bookForCheckInID = None
        self.search_string = None
        self.data = None

        self.searchLabel = Label(self.parent, text="Search here: Borrower ID, Borrower Name or ISBN")
        self.searchLabel.grid(row=0, column=0, padx=20, pady=20)
        self.searchTextBox = Entry(self.parent)
        self.searchTextBox.grid(row=1, column=0)
        self.searchBtn = Button(self.parent, text="Search", command=self.search_book_loans)
        self.searchBtn.grid(row=2, column=0)
        self.table = Treeview(self.parent, columns=["Loan ID", "ISBN", "Borrower ID", "Title"])
        self.table.grid(row=3, column=0)
        self.table.heading('#0', text="Loan ID")
        self.table.heading('#1', text="ISBN")
        self.table.heading('#2', text="Borrower ID")
        self.table.heading('#3', text="Book Title")
        self.table.bind('<ButtonRelease-1>', self.select_book_for_checkin)
        self.checkInBtn = Button(self.parent, text="Check In", command=self.check_in)
        self.checkInBtn.grid(row=4, column=0)

    def search_book_loans(self):
        self.search_string = self.searchTextBox.get()
        cursor = cnx.cursor()
        cursor.execute("select book_loans.LoanID, book_loans.ISBN, book_loans.Card_ID, book.title, book_loans.Date_In from book_loans "
                       "join borrower on book_loans.Card_ID = borrower.Card_ID "
                       "join book on book_loans.ISBN = book.ISBN "
                       "where book_loans.ISBN like concat('%', '" + self.search_string + "', '%') or "
                        "borrower.Fname like concat('%', '" + self.search_string + "', '%') or "
                        "borrower.Lname like concat('%', '" + self.search_string + "', '%') or "
                        "book_loans.Card_ID like concat('%', '" + self.search_string + "', '%')")

        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
        """
        View data on Treeview method.
        """
        self.table.delete(*self.table.get_children())
        for elem in self.data:
            if elem[4] is None:
                self.table.insert('', 'end', text=str(elem[0]), values=(elem[1], elem[2], elem[3]))

    def select_book_for_checkin(self, a):
        curItem = self.table.focus()
        self.bookForCheckInID = self.table.item(curItem)['text']

    def check_in(self):
        if self.bookForCheckInID is None:
            messagebox.showinfo("Attention!", "Select Book to Check In First!")
            return None
        cursor = cnx.cursor()
        cursor.execute("SELECT book_loans.Date_In FROM book_loans WHERE book_loans.LoanID = '" + str(self.bookForCheckInID) + "'")
        result = cursor.fetchall()
        if result[0][0] is None:
            cursor.execute("UPDATE book_loans SET book_loans.Date_In = '" + str(todays_date) + "' WHERE book_loans.LoanID = '"
                           + str(self.bookForCheckInID) + "'")
            cnx.commit()
            messagebox.showinfo("Done", "Book Checked In Successfully!")
            self.parent.destroy()
        else:
            return None
