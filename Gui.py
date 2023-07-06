import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from datetime import date
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview


from main import *
cnx = mysql.connector.connect(**{'user':'root','password':'tinytin03@21','host':'localhost','db':'Library'})


class GUI:
    def __init__(self, master):
        self.parent = master
        
        self.parent.title("Library Management System")
        self.frame = Frame(self.parent, width=1500, height=600)
        self.frame.grid(row=0, column=0)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_propagate(False)

        
        self.search_string = None
        self.data = None
        self.borrowerId = None
        self.bookForCheckOutIsbn = None

      
        self.HeaderFrame = Frame(self.frame)
        self.HeaderFrame.grid(row=0, column=0, sticky=N)
        self.HeaderFrame.grid_rowconfigure(0, weight=1)
        self.HeaderFrame.grid_columnconfigure(0, weight=1)
        
        
        self.HeaderLabel = Label(self.HeaderFrame, text='Search for books here')
        self.HeaderLabel.grid(row=0, column=0)
        self.HeaderLabel.grid_rowconfigure(0, weight=10)
        self.HeaderLabel.grid_columnconfigure(0, weight=10)
        
       
        self.SearchLabel = Label(self.HeaderFrame, text='')
        self.SearchLabel.grid(row=1, column=0)
        self.SearchLabel.grid_rowconfigure(1, weight=10)
        self.SearchLabel.grid_columnconfigure(0, weight=10)

        
        self.SearchFrame = Frame(self.frame)
        self.SearchFrame.grid(row=1, column=0, sticky=N)
        self.SearchFrame.grid_rowconfigure(1, weight=1)
       
        self.SearchLabel = Label(self.SearchFrame, text='Search')
        self.SearchLabel.grid(row=0, column=0)
        self.SearchLabel.grid_rowconfigure(0, weight=1)
       
        self.SearchTextBox = Entry(self.SearchFrame, text='Enter search string here...', width=70)
        self.SearchTextBox.grid(row=1, column=0)
        self.SearchTextBox.grid_rowconfigure(1, weight=1)
        self.SearchButton = Button(self.SearchFrame, text='Search', command=self.search)
        self.SearchButton.grid(row=3, column=0)
        self.SearchButton.grid_rowconfigure(3, weight=1)

      
        self.ActiveArea = Frame(self.frame)
        self.ActiveArea.grid(row=2, column=0, sticky=N)
        self.ActiveArea.grid_rowconfigure(2, weight=1)
        self.ResultTreeview = Treeview(self.ActiveArea, columns=["ISBN", "Book", "Author", "Availability"])
        self.ResultTreeview.grid(row=1, column=1)
        self.ResultTreeview.grid_rowconfigure(0, weight=1)
        self.ResultTreeview.heading('#0', text="ISBN")
        self.ResultTreeview.heading('#1', text="Book")
        self.ResultTreeview.heading('#2', text="Author")
        self.ResultTreeview.heading('#3', text="Availability")
        self.ResultTreeview.bind('<ButtonRelease-1>', self.selectBookForCheckout)

     
        self.MajorFunctions = Frame(self.frame)
        self.MajorFunctions.grid(row=3, column=0, sticky=N)
        self.MajorFunctions.grid_rowconfigure(3, weight=1)
        self.checkOutBtn = Button(self.MajorFunctions, text="Check Out ", bg='blue', command=self.check_out)
        self.checkOutBtn.grid(row=0, column=0, padx=10, pady=10)
        self.checkOutBtn.grid_rowconfigure(0, weight=1)
        self.checkOutBtn.grid_columnconfigure(0, weight=1)
        self.checkInBtn = Button(self.MajorFunctions, text="Check In ", command=self.check_in)
        self.checkInBtn.grid(row=1, column=0,padx=10, pady=10)
        self.checkOutBtn.grid_rowconfigure(0, weight=1)
        self.checkOutBtn.grid_columnconfigure(1, weight=1)
        self.updateFinesBtn = Button(self.MajorFunctions, text="Updates Fines", command=self.update_fines)
        self.updateFinesBtn.grid(row=0, column=2, padx=10, pady=10)
        self.payFinesBtn = Button(self.MajorFunctions, text="Pay Fines", command=self.pay_fines)
        self.payFinesBtn.grid(row=1, column=2, padx=10, pady=10)

        self.addBorrowerBtn = Button(self.MajorFunctions, text="Add Borrower", command=self.add_borrower)
        self.addBorrowerBtn.grid(row=0, column=1, padx=10, pady=10)

    def change_day(self):
        global todays_date
        todays_date = todays_date + timedelta(days=1)
        print(todays_date)

    def search(self):
        self.search_string = self.SearchTextBox.get()
        cursor = cnx.cursor()
        cursor.execute("select book.ISBN, book.title, authors.Name from book join book_author on "
                            "book.ISBN = book_author.isbn join authors on book_author.author_id = authors.author_id "
                            "where book.title like concat('%', '" + self.search_string + "', '%') or "
                            "authors.Name like concat('%', '" + self.search_string + "', '%') or "
                            "book.ISBN like concat('%', '" + self.search_string + "', '%')")

        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
        """
        View data on Treeview method.
        """
        self.ResultTreeview.delete(*self.ResultTreeview.get_children())
        for elem in self.data:
            cursor = cnx.cursor()
            cursor.execute("SELECT EXISTS(SELECT book_loans.ISBN from book_loans where book_loans.ISBN = '" + str(elem[0]) + "')")
            result = cursor.fetchall()
            if result == [(0,)]:
                availability = "Available"
            else:
                cursor = cnx.cursor()
                cursor.execute("SELECT book_loans.Date_In from book_loans where book_loans.ISBN = '" + str(elem[0]) + "'")
                result = cursor.fetchall()
                if result[-1][0] is None:
                    availability = "Not Available"
                else:
                    availability = "Available"
            self.ResultTreeview.insert('', 'end', text=str(elem[0]),
                                       values=(elem[1], elem[2], availability))

    def selectBookForCheckout(self, a):
        curItem = self.ResultTreeview.focus()
        self.bookForCheckOutIsbn = self.ResultTreeview.item(curItem)['text']

    def check_out(self):
        if self.bookForCheckOutIsbn is None:
            messagebox.showinfo("Book needs to be selected!")
            return None
        self.borrowerId = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
        cursor = cnx.cursor()
        cursor.execute("SELECT EXISTS(SELECT Card_ID from borrower WHERE borrower.Card_ID = '" + str(self.borrowerId) + "')")
        result = cursor.fetchall()

        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower not in Database!")
            return None
        else:
            count = 0
            cursor = cnx.cursor()
            cursor.execute("SELECT book_loans.Date_In from book_loans WHERE book_loans.Card_ID = '" + str(self.borrowerId) + "'")
            result = cursor.fetchall()
            for elem in result:
                if elem[0] is None:
                    count += 1
            if count >= 3:
                messagebox.showinfo("Not Allowed!", "Book Limit Exceeded!")
                return None
            else:
                cursor = cnx.cursor()
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                cursor.execute("INSERT INTO book_loans (ISBN, Card_ID, Date_out, Due_Date) VALUES ('" + self.bookForCheckOutIsbn + "', '" + self.borrowerId + "', '" + str(todays_date) + "', '" + str(todays_date + timedelta(days=14)) + "')")
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                cnx.commit()
                cursor = cnx.cursor()
                cursor.execute("SELECT MAX(LoanID) FROM book_loans")
                result = cursor.fetchall()
                loan_id = result[0][0]
                cursor.execute("INSERT INTO fines (Loan_Id, Fine_Amt, Paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
                cnx.commit()
                messagebox.showinfo("Done", "Book Loaned Out!")

    def check_in(self):
        self.checkInWindow = Toplevel(self.parent)
        self.checkInWindow.title("Do Check In here")
        self.app = CheckIn(self.checkInWindow)

    def update_fines(self):
        cursor = cnx.cursor()
        cursor.execute("SELECT book_loans.LoanID, book_loans.Date_In, book_loans.Due_Date FROM book_loans")
        result = cursor.fetchall()
        for record in result:
            date_in = record[1]
            date_due = record[2]
            if date_in is None:
                date_in = date.today()
            diff = date_in - date_due
            if diff.days > 0:
                fine = int(diff.days) * 0.25
            else:
                fine = 0
            cursor = cnx.cursor()
            cursor.execute("UPDATE fines SET fines.Fine_Amt = '" + str(fine) + "' WHERE fines.Loan_Id = '" + str(record[0]) + "'")
            cnx.commit()
        messagebox.showinfo("Info", "Generated Fines")

    def pay_fines(self):
        self.newPayFinesWindow = Toplevel(self.parent)
        self.newPayFinesWindow.title("Fines")
        self.app1 = PayFines(self.newPayFinesWindow)

    def add_borrower(self):
        self.newBorrowerWindow = Toplevel(self.parent)
        self.newBorrowerWindow.title("New Borrower")
        self.newapp = Borrower(self.newBorrowerWindow)
