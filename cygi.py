import streamlit as st
import os

# Set page configuration
st.set_page_config(
    page_title="Chatbot",
    page_icon=":robot_face:",
    layout="centered"
)

def get_response(question):
    if question == "Culture":
        return "Cygnet Digital offers diverse career growth opportunities, emphasizing knowledge sharing, collaboration, and employee excellence. With a supportive environment, continuous learning initiatives, and recognition programs, Cygnetians are empowered to excel and innovate within a dynamic community."
    elif question == "Corporate":
        return '''1. Cygnet Infotech Pvt. Ltd., IT Services & Solutions Provider Appraised at CMMI® Level 3  (The appraisal was performed by KPMG India – Transformation, Business Excellence) - January 30, 2024
        2. Cygnet Ushers in a New Era as Cygnet Digital, Powered by Innovative Framework: Cygnet COSMOS - October 25, 2023
        3. Cygnet Infotech Welcomes New Chief Operating Officer Narasimha to Drive Strategic Growth and Transformation. Narasimha brings a wealth of experience, having worked in the IT industry for over 25 years. He has held leadership positions in various reputed organizations, including IBM and Wipro, where he has honed his skills as a Business Leader, Chief Business & Operating Officer, Group Chief Delivery, Capabilities and Digital Officer, and Strategy and Transformation Expert. - April 21, 2023'''
    elif question == "Tax Technology":
        return '''1. GSTN is now onboarded as one of the FIPs (Financial Information Providers) on the Account Aggregator platform. The GSTN shall provide the details related to sales, outward Invoices, and tax payments. - December 15, 2022
        2. Cygnet TaxTech launches Vendor Postbox, a root cause fix to maximize Input tax credits - October 6, 2022
        3. Cygnet Infotech launches custom solution for start-ups and MSMEs to ensure compliance in a cost-effective manner - March 3, 2022'''
    elif question == "FinTech":
        return "Cygnet Infotech, a leading technology company with its clients across India, North America, Europe, the Middle East, and Africa, announced the grouping of its products and solutions for the Fintech space under the Cygnet Fintech brand. - May 13, 2022"
    elif question == "E-signature - Cygnature":
        return '''1. Cygnet Infotech Launches the Latest Version of Cygnature. The company has added a unique feature – the integration of UAE PASS, your secure national digital identity in the UAE, to support UAE based citizens to seamlessly use the digital signature solution for remote identification before consuming any online service. With UAE PASS, one can use different services across various sectors without the need to have multiple access credentials.- March 23, 2021
        2. In a recent research published by one of the leading business directories – TopDevelopers (USA), Cygnet Infotech has been ranked second globally in providing breakthrough blockchain solutions. The research was issued in San Francisco, California, USA. - January 11, 2021
        3. Cygnet Infotech Recognized as a Top Blockchain Technology Solution Provider by Digital Journal - February 14, 2019'''
    elif question == "Test Automation - TestingWhiz":
        return '''1. TestingWhiz has been rated as one of the best Testing Software of 2021 under Top 30 with a 4-star rating by G2! TestingWhiz was rated for Maintenance of test cases, Modularization of test cases, Effectiveness of tool, User-friendliness, Intuitive and lot more. - February 15, 2021
        2. The ultimate codeless test automation tool, TestingWhiz has released its latest version 7.1.1. (Uranus) on May 25th, 2020. Power-packed with a horde of pathbreaking features, exclusive enhancements and additional improvements to take your codeless test automation to the next level. - May 26, 2020
        3. Cygnet Infotech Tops the Cloud Testing Market – 2019 - February 25, 2019'''
    elif question == "What do we do":
        return '''Cygnet Digital offers comprehensive tax transformation services in India, UK & EU, and the Middle East, including E-invoicing, VAT returns, and data conversion. 
        Additionally, we provide finance transformation solutions like credit assessment platforms and digital lending systems, along with Account Aggregator solutions for leveraging aggregated data.'''
    elif question == "Services offered":
        return "Cygnet Digital offers a wide range of services spanning digital applications, product engineering, and enterprise application development. They specialize in API economy, cloud engineering, and application modernization. Their expertise extends to identity management, mobile engineering, and data analytics, covering data management, automation, and visualization. Additionally, they excel in digital commerce, offering unified commerce solutions, experience transformation, and expertise in Adobe and Salesforce platforms for enhanced customer experiences."
    elif question == "Mission":
        return "Our mission is to be a trusted digital transformation partner and consistently deliver Business Value to our Customers, Career Value to Cygnetians, Social Value to Communities."
    elif question == "Pinnacles":
        return '''1. 95% client retention rate
        2. 97% client satisfaction rate 
        3. 65% referral-based business 
        and many more...'''
    elif question == "COSMOS":
        return "Cygnet offers a comprehensive suite of business solutions under various initiatives like Nebula, Atlas, Aurora, Galaxy, and Comet. Leveraging Cygnet COSMOS, they facilitate co-ideation, co-innovation, and co-creation without upfront investments. With a focus on human-centric outcomes and industry expertise, Cygnet accelerates transformation journeys with speed to value through technology accelerators and frameworks like Cygnet Launchpad."
    elif question == "Digital Application and Product Engineering":
        return '''a. Backend - Microsoft (.net), .net (Core), Java, PHP, Hibernate, node JS, Spring, Python, Scala, Laravel
        b. Frontend - Java Script, React, Angular
        c. Mobile Technologies - React Native, Flutter, Swift, Quotlin
        d. Enterprise Applications - Microsoft Dynamics (CRM)
        e. IOT - Raspberry Pi, C++
        f. Blockchain - Hyperledger, Antchain
        g. Database - MYSQL, SQL server
        h. Testing - Acunetix, Apache jmeter, Testingwhiz (Cygnet)
        i. Cloud and DevOPS - Docker, AWS, Azzure'''
    elif question == "Enterprise Application and SAP":
        return '''a. Enterprise Applications - SAPP ECC, Salesforce
        b. Database - SAP HANA, Oracle, SQL Server
        c. Testing - Apache J meter
        d. Backend - Java, Hibernate, Spring'''
    elif question == "Data Analytics AI and Automation":
        return '''a. Backend - Python
        b. Frontend - Angular
        c. Database - SQL Server, MY SQL
        d. ETL and Data Visualization - Tableau, Power BI'''
    elif question == "Digital Commerce and Experience":
        return '''a. Backend - Python, PHP, Laravel
        b. DataBase - MY SQL
        c. Frontend - Java Script, Quotlin
        d. ETL and Data Visualization - AWS'''
    elif question == "Digital Transformation by Us in Next Gen Technologies":
        return "Innovative solutions across AI, multi-cloud, IoT, blockchain, and the metaverse drive efficiency and sustainability. AI-enabled POS reduces food wastage by 30%, while blockchain-enhanced traceability optimizes costs and reliability. IoT-based traffic management cuts congestion and emissions. Cygnature blockchain solution streamlines operations. Integrated ERP with AI/ML and blockchain boosts recycling facility efficiency. Azure's event management solution ensures availability and scalability."
    elif question == "Industries Living with Cygnet":
        return '''1. Finance and Insurance - HDFC Bank, the AI Corporation, Divide Buy, Spot, The Unlimited, BrightRock, Nobilex, RS Connect, Avant
        2. Manufacturing - Volkswagen, MG, Hitachi, Bosch, Tata Motors (Ignition Group),iBaset, jeldWen
        3. Healthcare - Lupin, Kepro, optioR, stryker, zevoHealth, Verofax
        4. Consumer - mondelez, LG, Landmark Group, Idox, Hindustan Uniliver, Roker, Disnep, Ziff Davis'''
    elif question == "Vision":
        return '''1. Value Based SLA, Integrated Delivery Model, Value Based Analytics, Flexible pricing model, Innovation Framework
        2. Improved Customer Experience, Optimized Operations, Reduced Time to Market, Business growth.
        3. Increased Revenue, Reduced TCO, Higher Efficiencies, Agility, Increased Working Capital'''
    elif question == "Business":
        return "Business transformation initiatives focus on enhancing visibility, speed to market, and intelligent enterprise integration, achieving 100% integration and cloudification. Intelligence transformation targets cost reductions, improved efficiency, and heightened business agility through automation and real-time decision-making. Experience transformation emphasizes higher product quality, value-based delivery, and connected experiences, ensuring seamless operations, continuous improvement, and enhanced customer interactions for sustained competitiveness."
    elif question == "Career":
        return '''1. 5+Years Cygnet Digital Academy
        2. 30 Average Age Gen Z & Millennials Population
        3. 4.2 Engagement Index Great Place to Work (Mar-22 to Mar-23)
        and many more...'''
    elif question == "Social":
        return '''1. 16 Bed ICCU Facility at Jivraj Mehta Hospital
        2. 700 Food Ration Kits Donated in the Pandemic
        3. 1000+ Digitally Literate Individuals
        and many more...'''
    elif question == "Certificate and Compliances":
        return '''1. HITRUST CSF Certified
        2. CMMIDEV/ 3
        3. ALCPA SOC2
        4. EU GDPR COMPLIANT
        5. ISO - 27001: 2013
        6. ISO - 9001: 2015'''
    elif question == "Awards and Recognitions":
        return '''1. Vibrant Gujarat Technology Summit
        2. The European Software Testing Awards
        3. Good Firms: Top Software Development Companies
        4. Top Developers - Top web and Software developers (2019)'''
    elif question == "Partnerships":
        return '''1. AWS Partner
        2. Microsoft Partner
        3. Bizz Pro
        4. Nobilex
        5. Multimedia Solutions
        6. SNC
        7. TPA Global
        8. Ignition
        9. Delodi
        10. Algorithmic Scale
        11. Hp Appliance One Member
        12. Adobe Solution Partner (Bronze Partner)
        13. ISTOB (Platinum Partner)
        14. AM Digital Life
        15. SAP (Silver Partner)'''
    elif question == "Contact Details for Queries":
        return '''1. HR: cygnetpxe@cygnet-digital.com
        2. HRD Alerts: HRDAlerts@cygnet-digital.com
        3. HR(personnel): akshay.kumar@cygnet-digital.com'''
    else:
        return "I'm sorry, I don't understand that"

def main():
    # Custom CSS for button styling
    st.markdown(
        """
        <style>
        /* Override Streamlit sidebar styles */
        .sidebar-content {
            background-color: #F0F8FF; /* Alice Blue*/
            color: black;
        }
        /* Override Streamlit main page styles */
        .stApp {
            background-color: #F0F8FF; /* Alice Blue*/
            color: black;
        }
        /* Override Streamlit button styles */
        .stButton>button {
            background-color: #5F9EA0; /* Cadet Blue */
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #2F4F4F; /* Dark Slate Grey*/
        }
        /* Override Streamlit sidebar styles */
        .sidebar-content {
            background-color: #F0F8FF; /* Alice Blue */
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Streamlit content
    st.title("Hi, I am Cygi!!!")
    st.write("How can I help you?")

    # Define categories and their corresponding questions
    categories = {
        "Goal": ["Mission", "Vision"],
        "Press Releases": ["Corporate", "Tax Technology", "FinTech", "E-signature - Cygnature", "Test Automation - TestingWhiz"],
        "Who Are We": ["Culture", "What do we do", "Services offered"],
        "Achievements": ["Certificate and Compliances", "Awards and Recognitions", "Pinnacles"],
        "Values": ["Business", "Career", "Social"],
        "Tie Ups": ["Industries Living with Cygnet", "Partnerships"],
        "Key Technologies": ["Digital Application and Product Engineering", "Enterprise Application and SAP", "Data Analytics AI and Automation", "Digital Commerce and Experience"],
        "Life Cycle": ["COSMOS", "Digital Transformation by Us in Next Gen Technologies"],
        "Contact Details": ["Contact Details for Queries"]
    }

    if 'stage' not in st.session_state:
        st.session_state.stage = 'category'

    if st.session_state.stage == 'category':
        st.write("Please select a category:")
        col1, col2, col3 = st.columns(3)
        for i, category in enumerate(categories):
            column = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
            if column.button(category):
                st.session_state.selected_category = category
                st.session_state.stage = 'question'

    elif st.session_state.stage == 'question':
        selected_category = st.session_state.selected_category
        st.subheader(selected_category)
        st.write("Please select a question:")
        selected_questions = categories[selected_category]
        for question in selected_questions:
            if st.button(question):
                st.session_state.selected_question = question
                st.session_state.stage = 'response'
        # Adding back button
        st.write("", "", text_align='center')  # Add empty lines to center align
        if st.button("Back"):
            st.session_state.stage = 'category'


    elif st.session_state.stage == 'response':
        selected_category = st.session_state.selected_category
        selected_question = st.session_state.selected_question
        st.subheader(selected_category)
        #st.write(f"Question: {selected_question}")
        response = get_response(selected_question)
        st.write(f"{response}")
        st.write("Would you like to ask another question?")
        if st.button("Yes"):
            st.session_state.stage = 'category'
        else:
            st.write("Thank you for using Cygi!")

# Call the main function to run the app
if __name__ == "__main__":
    main()
