# Usage Documentation for Checkmarx Expert Project

## Overview
The Checkmarx Expert Project provides functionality to identify and rectify vulnerabilities in C language code.

## Key Classes
1. **BaseAgent**: Base class for all agents.
2. **LLMAgent**: Inherits from BaseAgent and specializes in language models.
3. **CExpertAgent**: Specialized for C language code analysis.
4. **CheckmarxExpert**: Extends CExpertAgent to specifically target vulnerabilities and provide fixes.

## Running the Project
To run the project, simply execute `main.py` from the terminal. Ensure all dependencies are installed as specified in `requirements.txt`.

## Example Usage
The main features include:
- Identifying vulnerabilities in C code.
- Suggesting fixes.
- Auto-fixing common issues.
- Generating audit reports.

Refer to the source code and unit tests for detailed usage of individual classes and methods.