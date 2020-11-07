# -*- coding: utf-8 -*-
"""LSTM_with_FT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V2GVXXFDSN2yQFz1P0o-fM9VJ6VZwScX
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x

"""# Importing Libaries"""

#Import the libraries
import math
import pandas_datareader as web
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.python.keras.layers import Dense, LSTM, Dropout
from tensorflow.python.keras import Sequential
import matplotlib.pyplot as plt
from tensorflow.keras import optimizers
plt.style.use('fivethirtyeight')
import pywt

"""# Reading Dataset-1"""

dataset_1 = pd.read_csv("/content/GS.csv")
df= dataset_1.copy()
df=df.dropna()
df=df[['Date','Close','Open','Low', 'High','Volume','Close_JPM','Close_MS']]
df['Date'] = pd.to_datetime(df['Date'])
df.index= df['Date']
df=df.drop(columns=['Date'])
df=df.head(2500)
df
#df=df.drop(columns=['Date','Prev Close','Last Price','Average Price'])
#df.rename(columns={0:"Low", 1:"High", 2:"Open", 3:"Close", 4:"Volume"}, inplace=True)

"""# Reading Dataset-2"""

dataset_1 = pd.read_csv("/content/APOLLOTYRE__EQ__NSE__NSE__MINUTE.csv")
dataset_1= dataset_1.drop(columns = ['open'])
dataset_1 = dataset_1.drop(columns = ['high'])
dataset_1 = dataset_1.drop(columns = ['low'])
dataset_1 = dataset_1.drop(columns = ['volume'])
df= dataset_1.copy()
df=df.dropna()
#df=df[['Date','Low Price', 'High Price','Open Price', 'Close Price', "No. of Trades"]]
#df['timestamp'] = pd.to_datetime(df['timestamp'])
df.index= df['timestamp']
df=df.drop(columns=['timestamp'])
df['Close']=df['close']
#df=df.tail(150000)
#df=df.head(12000)
df=df.tail(5000)
df=df.head(2000)
df

"""# Reading Dataset-3"""

#Get the stock quote
df = web.DataReader('AAPL', data_source='yahoo', start='2012-01-01', end='2019-12-17')
#Show teh data
df

"""# Visualization of Dataset"""

#Visualize the closing price history
plt.figure(figsize=(28,8))
plt.title('Close Price History')
df['Close'].plot()
#plt.plot(df['Close'])
plt.xlabel('Date & time', fontsize=18)
plt.ylabel('Close Price', fontsize=18)
plt.show()

#Create a new dataframe with only the 'Close column
data = df.filter(['Close','Open','Low', 'High','Close_JPM','Close_MS'])
data

"""# Fourier Transform"""

data_FT = data
close_fft = np.fft.fft(np.asarray(data_FT['Close'].tolist()))
fft_df = pd.DataFrame({'fft':close_fft})
fft_df['absolute'] = fft_df['fft'].apply(lambda x: np.abs(x))
fft_df['angle'] = fft_df['fft'].apply(lambda x: np.angle(x))

plt.figure(figsize=(20, 8), dpi=100)
fft_list = np.asarray(fft_df['fft'].tolist())
for num_ in [3, 6, 9, 100]:
    fft_list_m10= np.copy(fft_list); fft_list_m10[num_:-num_]=0
    plt.plot(np.fft.ifft(fft_list_m10), label='Fourier transform with {} components'.format(num_))
plt.plot(data_FT['Close'].values,  label='Real')
plt.xlabel('Days')
plt.ylabel('Price')
plt.title('Figure 3:stock prices & Fourier transforms')
plt.legend()
plt.show()

num_=3
fft_list_m10= np.copy(fft_list); fft_list_m10[num_:-num_]=0
temp=np.fft.ifft(fft_list_m10)
temp=np.real(temp)
data['fft']=temp
data.head()

num_=6
fft_list_m10= np.copy(fft_list); fft_list_m10[num_:-num_]=0
temp=np.fft.ifft(fft_list_m10)
temp=np.real(temp)
data['fft6']=temp
data.head()

num_=9
fft_list_m10= np.copy(fft_list); fft_list_m10[num_:-num_]=0
temp=np.fft.ifft(fft_list_m10)
temp=np.real(temp)
data['fft9']=temp
data.head()

num_=15
fft_list_m10= np.copy(fft_list); fft_list_m10[num_:-num_]=0
temp=np.fft.ifft(fft_list_m10)
temp=np.real(temp)
data['fft15']=temp
data.head()

"""# Technical Indicators"""

def get_technical_indicators(dataset):
    # Create 7 and 21 days Moving Average
    dataset['ma7'] = dataset['Close'].rolling(window=7).mean().fillna(0)
    dataset['ma7'][0:7]=dataset['Close'][0:7]
    dataset['ma21'] = dataset['Close'].rolling(window=21).mean().fillna(0)
    dataset['ma21'][0:21]=dataset['Close'][0:21]
    # Create MACD
#    dataset['26ema'] = pd.ewm(dataset['Close'], span=26)
#    dataset['12ema'] = pd.ewm(dataset['Close'], span=12)
#    dataset['MACD'] = (dataset['12ema']-dataset['26ema'])

    # Create Bollinger Bands
#    dataset['20sd'] = pd.stats.moments.rolling_std(dataset['Close'],20)
#    dataset['upper_band'] = dataset['ma21'] + (dataset['20sd']*2)
#    dataset['lower_band'] = dataset['ma21'] - (dataset['20sd']*2)
    
    # Create Exponential moving average
#    dataset['ema'] = dataset['Close'].ewm(com=0.5).mean()
    
    # Create Momentum
#    dataset['momentum'] = dataset['Close']-1
    
    return dataset

data = get_technical_indicators(data)
data.head(8)

#Convert the dataframe to a numpy array
dataset = data.values
#Get the number of rows to train the model on
training_data_len = math.ceil( len(dataset) * .8)

training_data_len
print(dataset.shape)

"""# MinMax Scaling"""

#Scale the data
scaler1 = MinMaxScaler(feature_range=(0,1))
d1=dataset[:,0].reshape(-1,1)
scaled_data_1 = scaler1.fit_transform(d1)
scaler2 = MinMaxScaler(feature_range=(0,1))
d2=dataset[:,1:]
scaled_data_2 = scaler2.fit_transform(d2)
scaled_data=np.column_stack((scaled_data_1,scaled_data_2))

"""# Visualization of all features used for training"""

plt.figure(figsize=(16,8))
plt.title('Training Features--GS')
plt.plot(data)
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price', fontsize=18)
plt.show()

print (data)

"""# Making dataset suitable for LSTM"""

#Create the training data set
#Create the scaled training data set
train_data = scaled_data[0:training_data_len , :]
#Split the data into x_train and y_train data sets
x_train = []
y_train = []

for i in range(60, len(train_data)):
  x_train.append(train_data[i-60:i])
  y_train.append(train_data[i, 0])
  if i<= 61:
    print(x_train)
    print(y_train)
    print()

"""#"""

#Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

#Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], x_train.shape[2]))
x_train.shape

#Create the testing data set 
test_data = scaled_data[training_data_len - 60: , :]
#Create the data sets x_test and y_test
x_test = []
y_test = dataset[training_data_len:,0]
y_test_scaled=scaled_data[training_data_len:,0]
for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i])
 # y_test_scaled.append(train_data[i, 0])
#Convert the data to a numpy array
x_test = np.array(x_test)
#Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], x_test.shape[2] ))

"""# LSTM Model"""

#Build the LSTM model
model = Sequential()
model.add(LSTM(200, return_sequences=True, input_shape= (x_train.shape[1], x_train.shape[2])))
model.add(Dense(50))
model.add(Dropout(0.5))
model.add(LSTM(60, return_sequences= True))
model.add(Dropout(0.5))
model.add(LSTM(30, return_sequences= True))
model.add(Dropout(0.5))
model.add(LSTM(30, return_sequences= False))
model.add(Dropout(0.5))
model.add(Dense(25))
model.add(Dense(1))
#Compile the model
sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
rmsprop=optimizers.RMSprop(lr=0.01, rho=0.9)
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()
#Train the mode
hist=model.fit(x_train, y_train, batch_size=194, epochs=180,validation_data=(x_test,y_test_scaled),shuffle=False)

plt.figure(figsize=(10,6),dpi=100)
plt.plot(hist.history['loss'],label='lstm_train',color='red')
plt.plot(hist.history['val_loss'],label='lstm_test',color='green')
plt.xlabel('epochs')
plt.ylabel('loss')

#Get the models predicted price values 
predictions = model.predict(x_test)

"""# Error Calculation"""

rmse=np.sqrt(np.mean(((predictions- scaled_data[training_data_len:,0 ])**2)))
print(rmse)
predictions = scaler1.inverse_transform(predictions)
#Get the root mean squared error (RMSE)
rmse=np.sqrt(np.mean(((predictions- y_test)**2)))
print(rmse)

"""# Visualization of Predictions"""

train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions
#Visualize the data
plt.figure(figsize=(16,8))
plt.title('Model')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)

plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
#train['Close'].plot()
#valid[['Close', 'Predictions']].plot()
plt.legend(['Train', 'Test', 'Predictions'], loc='upper right')
plt.show()

plt.figure()
plt.ylabel('Close Price USD ($)', fontsize=18)
valid['Close'].plot(legend=True, color='red')
valid['Predictions'].plot(legend=True, color='yellow', figsize=(25,9))
#plt.plot(valid[['Close', 'Predictions']],figsize=(20,8))

"""# Correlation Coefficient Calculation"""

#Show the valid and predicted prices
valid
k1=np.corrcoef(valid['Close'],valid['Predictions'])
print (k1[0][1])
