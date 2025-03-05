from tkinter import *  
from PIL import ImageTk
import tkinter as tk
from tkinter import Button
from tkinter import messagebox
import psycopg2
def clear():
    emailEntry.delete(0,END)
    UsernameEntry.delete(0,END)
    MobileEntry.delete(0,END)
    PasswordEntry.delete(0,END)
    ConfirmPasswordEntry.delete(0,END)
    check.set(0)
def connect_database():
    if emailEntry.get()=='' or UsernameEntry.get()=='' or MobileEntry.get()=='' or PasswordEntry.get()=='' or ConfirmPasswordEntry.get()=='':
        messagebox.showerror('Error','All Fields Are Required')
    elif PasswordEntry.get() != ConfirmPasswordEntry.get():
        messagebox.showerror('Error','Password Mismatched')
    elif check.get( )==0:
        messagebox.showerror('Error','Please Accept Terms And Conditions')
    else:
        #try:
          #con=psycopg2.connect(database='customer',host='localhost',user='postgres',password='12345',port='5432')
          #mycursor=con.cursor()
          
         
        #except:
            #messagebox.showerror('Error','Database Connectivity Issue')
            #return         
            #query='create database customer'
            #mycursor.execute(query)
        #query='use customer'
        #mycursor.execute(query)
        #query='create table details(Customer_id Serial primary key not null,email varchar(30),username varchar(100),mobilenumber BIGINT,password varchar(20))'
        #mycursor.execute(query)
        #con.commit()
        
    # Step 1: Connect to PostgreSQL database
        con = psycopg2.connect(database="customer",host="localhost",user="postgres",password="12345",port="5432")
        mycursor = con.cursor()
    # Step 2: Create the table (if not exists)
        query = 'CREATE TABLE IF NOT EXISTS details (Customer_id SERIAL PRIMARY KEY,email VARCHAR(30) UNIQUE,username VARCHAR(100),mobilenumber VARCHAR(15),password VARCHAR(20));'
        mycursor.execute(query)
        query='select * from details where username = %s'
        mycursor.execute(query,(UsernameEntry.get(),))
        r=mycursor.fetchone()
        if r is not None:
            messagebox.showerror('Error','UserName Already Exists')
        else:
            query='insert into details(email,username,mobilenumber,password) values (%s,%s,%s,%s)'
            mycursor.execute(query,(emailEntry.get(),UsernameEntry.get(),MobileEntry.get(),PasswordEntry.get()))
            con.commit()
            messagebox.showinfo('Success','Registration is Successful')
            #messagebox.showinfo('Success','Registration is Successful')
            clear()
            sign_window.destroy()
            import Login_window    
            
            mycursor.close()
            con.close()
       #except:
        #messagebox.showerror("Error", "Database Connectivity Issue")

def login_page():
    sign_window.destroy()
    import Login_window

sign_window = tk.Tk()
sign_window.title("Login UI")
sign_window.geometry('900x600')
sign_window.resizable(0,0)

background=ImageTk.PhotoImage(file="C:\\Users\\aleem\\Downloads\\WhatsApp Image 2025-03-03 at 7.44.59 PM.jpeg")
bglabel=Label(sign_window,image=background)
bglabel.grid()
bglable=(80,50)
frame = Frame(sign_window)
frame.place(x=535,y=15)

heading = Label(frame,text="CREATE AN ACCOUNT",font=('Montserrat',20,'bold'),fg="Royalblue4")
heading.grid(row=0,column=0,padx=25,pady=10)

emaillabel=Label(frame,text='Email : ',font=('Montserrat',14,'bold'),fg="Royalblue4")
emaillabel.grid(row=1,column=0,sticky='w',padx=2,pady=(10,0))

emailEntry = Entry(frame,width=30,font=('Montserrat',14,'bold'))
emailEntry.grid(row=2,column=0,sticky='w',padx=5)

Username=Label(frame,text='Username : ',font=('Montserrat',14,'bold'),fg="Royalblue4")
Username.grid(row=3,column=0,sticky='w',padx=2,pady=(10,0))

UsernameEntry = Entry(frame,width=30,font=('Montserrat',14,'bold'))
UsernameEntry.grid(row=4,column=0,sticky='w',padx=5)

MobileNumber=Label(frame,text='Mobile Number :',font=('Montserrat',14,'bold'),fg="Royalblue4")
MobileNumber.grid(row=5,column=0,sticky='w',padx=2,pady=(10,0))

MobileEntry = Entry(frame,width=30,font=('Montserrat',14,'bold'))
MobileEntry.grid(row=6,column=0,sticky='w',padx=5)  

Password=Label(frame,text='Password : ',font=('Montserrat',14,'bold'),fg="Royalblue4")
Password.grid(row=7,column=0,sticky='w',padx=2,pady=(10,0))

PasswordEntry = Entry(frame,width=30,font=('Montserrat',14,'bold'))
PasswordEntry.grid(row=8,column=0,sticky='w',padx=5)

ConfirmPassword=Label(frame,text='Confirm Password : ',font=('Montserrat',14,'bold'),fg="Royalblue4")
ConfirmPassword.grid(row=9,column=0,sticky='w',padx=2,pady=(10,0))

ConfirmPasswordEntry = Entry(frame,width=30,font=('Montserrat',14,'bold'))
ConfirmPasswordEntry.grid(row=10,column=0,sticky='w',padx=5)

check=IntVar()
termsandcondition=Checkbutton(frame,text='I agree to terms & conditons',font=('Montserrat',14,'bold'),activebackground='gainsboro',activeforeground='RoyalBlue4',cursor='hand2',variable=check,fg="Royalblue4")
termsandcondition.grid(row=11,column=0,sticky='w',padx=2,pady=15)

SignupButton=Button(frame,text="Signup",font=('Open sans',14,'bold'),bd=0,fg='Royalblue4',activebackground='RoyalBlue4',activeforeground='white',command=connect_database)
SignupButton.grid(row=12,column=0,sticky='w',padx=115,pady=(9,0))

Signuplabel = Label(frame,text="Already have an Account?",font=('Open Sans',12,'bold'),fg="Royalblue4")
Signuplabel.grid(row=13,column=0,sticky='w',padx=5,pady=(10,0))

createnewbutton = Button(frame,text="Log in",font=('Open Sans',11 ,'bold underline'),activebackground='white',cursor="hand2",activeforeground='blue',bd=0,command=login_page,fg="Royalblue4")
createnewbutton.place(x=210,y=493)

sign_window.mainloop()
