from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)

# Проблемные данные диаграмма
data_problem = {
    "Дата": ["2025-03-20", "2025-03-21", "2025-03-22", "2025-03-23", "2025-03-24"],
    "Backlog": [15, 18, 20, 22, 25],
    "To Do": [10, 12, 13, 14, 15],
    "In Progress": [8, 10, 12, 14, 16],
    "Review": [5, 6, 7, 8, 9],
    "Done": [2, 2, 3, 3, 4]
}

# Хорошие данные
data_good = {
    "Дата": ["2025-03-20", "2025-03-21", "2025-03-22", "2025-03-23", "2025-03-24"],
    "Backlog": [10, 8, 6, 4, 2],
    "To Do": [5, 4, 3, 2, 1],
    "In Progress": [3, 3, 2, 2, 2],
    "Review": [2, 1, 1, 1, 1],
    "Done": [0, 3, 6, 9, 12]
}

# Функция для подготовки данных
def prepare_data(data):
    df = pd.DataFrame(data)
    df["Дата"] = pd.to_datetime(df["Дата"])
    df.set_index("Дата", inplace=True)
    df["WIP"] = df["In Progress"] + df["Review"]
    df["Throughput"] = df["Done"].diff().fillna(df["Done"])
    df["Arrival Rate"] = df["Backlog"].diff().fillna(df["Backlog"]) * -1
    df["Cycle Time"] = df["WIP"] / df["Throughput"].replace(0, 1)
    return df

# Генерация графиков
def generate_cfd_chart(df, title):
    fig = px.area(df, x=df.index, y=["Backlog", "To Do", "In Progress", "Review", "Done"],
                  labels={"value": "Количество задач", "variable": "Этапы"},
                  title=title)
    return fig.to_html(full_html=False)

def generate_metrics_chart(df, title):
    fig = px.line(df, x=df.index, y=["WIP", "Throughput", "Arrival Rate"],
                  markers=True, title=title)
    return fig.to_html(full_html=False)

def generate_cycle_time_chart(df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Cycle Time"], mode='lines+markers', name="Cycle Time"))
    fig.update_layout(title=title, xaxis_title="Дата", yaxis_title="Дни")
    return fig.to_html(full_html=False)

@app.route("/")
def index():
    df_problem = prepare_data(data_problem)
    df_good = prepare_data(data_good)
    
    return render_template("index.html",
                           cfd_chart_problem=generate_cfd_chart(df_problem, "CFD: Проблемные показатели"),
                           metrics_chart_problem=generate_metrics_chart(df_problem, "Метрики: Проблемные показатели"),
                           cycle_time_chart_problem=generate_cycle_time_chart(df_problem, "Cycle Time: Проблемные показатели"),
                           cfd_chart_good=generate_cfd_chart(df_good, "CFD: Хорошие показатели"),
                           metrics_chart_good=generate_metrics_chart(df_good, "Метрики: Хорошие показатели"),
                           cycle_time_chart_good=generate_cycle_time_chart(df_good, "Cycle Time: Хорошие показатели"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)