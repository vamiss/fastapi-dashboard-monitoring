import psutil
import pandas as pd

CPU_COUNT = psutil.cpu_count()

df = pd.DataFrame()

for i in range(CPU_COUNT):
    df[f'cpu{i+1}'] = [0.0] * 300
df['ram'] = [0.0] * 300

def update_df():
    
    df.iloc[:-1, :] = df.iloc[1:, :]
    df.iloc[-1, :-1] = psutil.cpu_percent(percpu=True)

    # df.iloc[:-1, -1] = df.iloc[1:, -1]
    df.iloc[-1, -1] = psutil.virtual_memory().percent


# def update_df_ram():

#     df.iloc[:-1, -1] = df.iloc[1:, -1]
#     df.iloc[-1, -1] = psutil.virtual_memory().percent