import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import os
import requests

# Set OpenAI API key and Proxy
openai.api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMxMDAwMDc1QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.gE2pC5vPidH1Y4M8ZB7zY-YOPJJ-Jw_CNMUlD9C7974"  # Replace with your OpenAI API key

#proxies = {
#    "http": "http://aiproxy.sanand.workers.dev/openai",
#    "https": "http://aiproxy.sanand.workers.dev/openai",
#}

url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {openai.api_key}",
    "Content-Type": "application/json"
}


# Step 1: Analyze Dataset
def analyze_dataset(file_path):
    data = pd.read_csv(file_path,encoding='ISO-8859-1')
    summary = {
        "num_rows": len(data),
        "num_columns": len(data.columns),
        "columns": data.dtypes.to_dict(),
        "missing_values": data.isnull().sum().to_dict(),
    }
    return data, summary

# Step 2: Generate Visualizations
def visualize_data(data):
    visualizations = []
    output_dir = "./"  # Save charts in the current directory

    # Plot numeric columns
    numeric_columns = data.select_dtypes(include=['number']).columns
    if len(numeric_columns) > 0:
        for col in numeric_columns[:3]:  # Limit to 3 charts
            plt.figure(figsize=(10, 6))
            plt.hist(data[col].dropna(), bins=20, alpha=0.7, color='blue', label=col)
            plt.title(f"Distribution of {col}")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            plt.legend()
            plot_path = os.path.join(output_dir, f"{col}_distribution.png")
            plt.savefig(plot_path)
            visualizations.append(plot_path)
            plt.close()

    # Plot categorical columns
    categorical_columns = data.select_dtypes(include=['object']).columns
    if len(categorical_columns) > 0:
        for col in categorical_columns[:3 - len(visualizations)]:  # Ensure max 3 charts
            plt.figure(figsize=(12, 6))
            sns.countplot(data=data, x=col, order=data[col].value_counts().index[:10])
            plt.title(f"Top 10 Categories in {col}")
            plt.xticks(rotation=45, ha='right')
            plt.xlabel(col)
            plt.ylabel("Count")
            plot_path = os.path.join(output_dir, f"{col}_distribution.png")
            plt.savefig(plot_path)
            visualizations.append(plot_path)
            plt.close()

    return visualizations

# Step 3: Narrate with OpenAI LLM via Proxy
def narrate_with_llm(summary, visualizations):
    prompt = (
        f"Analyze the following dataset summary and provide a detailed narrative:\n"
        f"Number of rows: {summary['num_rows']}\n"
        f"Number of columns: {summary['num_columns']}\n"
        f"Column data types: {summary['columns']}\n"
        f"Missing values per column: {summary['missing_values']}\n\n"
        f"Explain patterns, trends, and anomalies in the data and suggest potential use cases."
    )

    data = {
    "model":"gpt-4o-mini",
    "messages":[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": prompt}
            ]
    } 

    try:
        response = requests.post(url, headers=headers,json=data)
        #return response
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating narrative: {e}"

# Step 4: Generate README.md
def generate_readme(narrative, visualizations):
    with open("README.md", "w") as readme_file:
        # Add Title and Narrative
        readme_file.write("# Automated Data Analysis Report\n\n")
        readme_file.write("## Narrative\n\n")
        readme_file.write(narrative)

        # Add Visualizations
        readme_file.write("## Visualizations\n\n")
        for vis_path in visualizations:
            filename = os.path.basename(vis_path)
            readme_file.write(f"![{filename}]({filename})\n\n")

# Main Function
def main(file_path):
    data, summary = analyze_dataset(file_path)
    visualizations = visualize_data(data)
    narrative = narrate_with_llm(summary, visualizations)
    generate_readme(narrative, visualizations)
    print("Analysis complete. Results saved in README.md and associated .png files.")

# Example Usage
file_path = "/content/happiness.csv"  # Replace with your dataset file path
main(file_path)

