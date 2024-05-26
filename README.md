# Org Chart Helper
**Leveraging AI for efficient org chart management**

## What is Org Chart Helper?
Org Chart Helper is an AI-powered tool designed to help organizations effectively access and manage their organizational hierarchy. It provides a seamless way to generate org charts for the entire organization or specific managers, teams, or departments. The application simplifies the process of querying organizational relationships and employee information, making it a useful tool for HR teams and managers.

## Simple Data Integration
Org Chart Helper requires a basic "database" in the form of a CSV file containing employee information and reporting relationships. The minimal data file needs just three columns:
- Employee Name
- Report To
- Job Title
Additional columns like Department, Start Date, and more can be included as needed to enrich the data. You can use the sample [employees.csv](employees.csv) as a starting point.

## Technology Stack
Org Chart Helper utilizes [Chainlit](https://chainlit.io/) for the front-end interface and OpenAI or Azure OpenAI APIs at the backend. It leverages the latest GPT model (GPT-4o) with a lower temperature setting (0.5) to ensure more accurate outcomes. The application also employs function calling (tools) to enhance its capabilities.

To generate the org charts, the application uses Generative AI to create chart data in DOT language, which is then rendered using [Graphviz](https://graphviz.org/).

## Versatile Query Capabilities
### Query reporting relationships (e.g., "Who reports to whom?")
<img src="/images/reporting_relationship.png" alt="Query reporting relationships"></img>


### Generate org charts for a selected manager, team, or group
<img src="/images/generate_org_chart.png" alt="Generate org chart"></img>

<img src="/images/generated_chart.png" alt="Generated org chart"></img>


### Query employee information (e.g., job title, start date) as long as the information is present in the data file
<img src="/images/query_employee_information.png" alt="Query employee information"></img>


### Update the employee data file
<img src="/images/update_employees_file.png" alt="Update the employee data file"></img>

## Instructions:
- Clone the source code:
```bash
git clone https://github.com/skydockAI/org_chart_helper.git
```

- Install required libraries:
```bash
pip install -r requirements.txt
```

- Install [Graphviz](https://graphviz.org/) if needed

- Replace the sample data file [employees.csv](employees.csv) with your actual employees data

- Open [app.py](app.py) and setup your OpenAI or Azure OpenAI API keys

- Run the application:
```bash
chainlit run app.py
```

## Limitations
While Org Chart Helper offers a robust set of features, it is not without limitations. One known issue is the AI's difficulty with accurate counting. The model may provide incorrect answers when asked to count the total number of employees or the number of reports a manager has. This will be addressed in the next update.

## License:
**Org Chart Helper** is open-source and licensed under the [GPL-3.0](LICENSE) license.
