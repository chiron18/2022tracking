import pandas as pd
import streamlit as st
import numpy as np
import io



def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


st.set_page_config(layout="wide")

def appendDictToDF(df,dictToAppend):
  df = pd.concat([df, pd.DataFrame.from_records([dictToAppend])])
  return df

def expenses():
    file = '2022_expenses.csv'
    return file

def payments():
    file = '2022_payments.csv'
    return file

EXPENSE_FILE=expenses()
PAYMENT_FILE=payments()

input_df = pd.read_csv(EXPENSE_FILE)  
payments_df=pd.read_csv(PAYMENT_FILE)

input_df['Paid']=input_df['Paid'].astype(float)
input_df['Paid']=input_df['Paid'].round(2)
payments_df['Amount']=payments_df['Amount'].astype(float)
payments_df['Amount']=payments_df['Amount'].round(2)

expenses_df = input_df.copy()
expenses_df['count'] = expenses_df[['Greg', 'Ian', 'Jerry','Peter']].sum(axis=1)
expenses_df['amount'] = expenses_df['Paid']/expenses_df['count'] 
expenses_df['amount']=expenses_df['amount'].astype(float)
expenses_df['amount']=expenses_df['amount'].round(2)

owes_df = pd.DataFrame(columns=['Situation','Amount', 'Item']) # create empty dataframe

for row in range(0,expenses_df.shape[0]):
    for people in range(3,7):
        item = expenses_df.iat[row,0]
        paid = expenses_df.iat[row,1]
        paid_by = expenses_df.iat[row,2]
        count = expenses_df.iat[row,8]
        amount = paid/count
        debtor = expenses_df.columns[people]
        situation = debtor + " owes " + paid_by

        if (expenses_df.iat[row,people] == True):
            owes_df= appendDictToDF(owes_df,{'Situation':situation,'Amount': amount, 'Item': item })

for row in range(0,payments_df.shape[0]):
    payer = payments_df.iat[row,0]
    print(payer)
    payee = payments_df.iat[row,1]
    payment = payments_df.iat[row,2]
    item = "payment"
    situation = payee + " owes " + payer
    owes_df= appendDictToDF(owes_df,{'Situation':situation,'Amount': payment, 'Item': item })

group_owe = owes_df.groupby(['Situation'], as_index = False)['Amount'].sum()
lookup = group_owe.copy()
group_owe['Alternate'] = group_owe.Situation.str.split(' owes ').str[1] +" owes " + group_owe.Situation.str.split(' owes ').str[0]
mapLookup = dict(lookup[['Situation', 'Amount']].values)
group_owe['Alternate Amount'] = group_owe['Alternate'].map(mapLookup)
group_owe['Alternate Amount'] = group_owe['Alternate Amount'].replace(np.nan, 0)
group_owe['Final Amount']=group_owe['Amount'] -group_owe['Alternate Amount']
group_owe = group_owe[group_owe['Final Amount'] > 0]
group_owe['Amount']=group_owe['Amount'].round(2)
group_owe['Final Amount']=group_owe['Final Amount'].round(2)

final_owe = group_owe.copy()
final_owe = final_owe.drop(['Amount', 'Alternate', 'Alternate Amount'], axis=1)

page_bg_img = """
<style>
[data-testid="block-container"]{
background-image: url(https://gunsmagazine.com/wp-content/uploads/2022/07/G1022-Marlin-1895_Open-Action-7158_HR.jpg);
background-size: cover;
background-position: right left;
background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.header('2022 Expense Tracking')

with open("hunt.css") as source_des:
    st.markdown(f"<style>{source_des.read()}</style>", unsafe_allow_html=True)

st.write("Expenses Submitted")
st.caption('Enter expense details, the checkmarks under names indicate the persons that will share the expense')
edited_df = st.data_editor(input_df, num_rows = "dynamic")

st.write("Payments Made")
st.caption('Enter payment details')
payment_edited_df = st.data_editor(payments_df, num_rows = "dynamic")



if st.button('Save Changes (manually refresh page to update final tally)'):
    edited_df.to_csv(EXPENSE_FILE, index=False)
    payment_edited_df.to_csv(PAYMENT_FILE, index=False)

st.write("Final Tally")
st.dataframe(final_owe, hide_index=True)

st.write("")
st.write("")
st.write("")
st.write("working dataframes")

st.write(owes_df)
st.write(group_owe)
st.write(expenses_df)

