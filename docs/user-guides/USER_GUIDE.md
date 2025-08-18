# Claims Triage AI - User Guide

## Getting Started

### First Time Setup

1. **Access the Platform**
   - Open your web browser
   - Navigate to: `http://localhost:3000` (development) or your production URL
   - You will see the login screen

2. **Create Your Account**
   - Click "Register" if you don't have an account
   - Fill in your details:
     - Username: Choose a unique username
     - Email: Your work email address
     - Password: Create a strong password
     - Role: Select your role (Agent, Manager, Admin)
   - Click "Create Account"

3. **Log In**
   - Enter your username and password
   - Click "Sign In"
   - You'll be redirected to the dashboard

### Dashboard Overview

The dashboard provides a comprehensive view of your case triage operations:

#### Key Metrics
- **Total Cases**: Number of cases in the system
- **Pending Cases**: Cases awaiting processing
- **SLA Compliance**: Percentage of cases meeting SLA targets
- **Average Processing Time**: Time to complete case triage

#### Quick Actions
- **Create New Case**: Start a new case triage
- **View Queue**: See pending cases
- **Analytics**: Access detailed reports
- **Settings**: Configure your preferences

## Case Management

### Creating a New Case

1. **Navigate to Case Creation**
   - Click "Create Case" from the dashboard
   - Or go to "Triage Queue"  "New Case"

2. **Fill in Case Details**
   - **Title**: Brief, descriptive case title
   - **Description**: Detailed case description
   - **Case Type**: Select appropriate category:
     - Auto Insurance
     - Health Insurance
     - Property Insurance
     - Credit Dispute
     - Legal Case
   - **Urgency Level**: Choose urgency:
     - Low: Standard processing
     - Medium: Expedited processing
     - High: Priority processing
     - Critical: Immediate attention
   - **Amount**: Financial amount involved (if applicable)
   - **Additional Metadata**: Any relevant information

3. **Submit Case**
   - Click "Create Case"
   - The system will automatically start the triage process
   - You'll be redirected to the case details page

### Viewing Case Details

The case details page shows comprehensive information:

#### Case Information
- **Basic Details**: Title, description, type, urgency
- **Status**: Current processing status
- **Timeline**: Creation and update timestamps
- **Metadata**: Additional case information

#### Triage Results
- **Classification**: AI-determined case type and urgency
- **Risk Assessment**: Risk score and level
- **Routing**: Recommended team and SLA
- **Decision Support**: Suggested actions and templates
- **Compliance**: PII detection and audit information

#### Case History
- **Triage Runs**: All triage processing attempts
- **Status Changes**: Case status updates
- **User Actions**: Manual interventions and updates

### Managing Cases

#### Updating Case Information
1. Click "Edit" on the case details page
2. Modify the relevant fields
3. Click "Save Changes"
4. The system will log the update in the audit trail

#### Case Status Management
- **Assign to Team**: Route case to appropriate team
- **Change Status**: Update case status (New  In Progress  Completed)
- **Add Notes**: Include additional context or instructions
- **Escalate**: Flag for immediate attention

#### Bulk Operations
- **Select Multiple Cases**: Use checkboxes to select cases
- **Bulk Assign**: Assign multiple cases to a team
- **Bulk Status Update**: Update status for multiple cases
- **Export**: Export case data for external processing

## Triage Queue Management

### Understanding the Queue

The triage queue shows all cases awaiting processing:

#### Queue Views
- **All Cases**: Complete case list
- **Pending**: Cases awaiting triage
- **In Progress**: Cases being processed
- **Completed**: Finished cases
- **Overdue**: Cases exceeding SLA

#### Filtering and Sorting
- **Filter by Type**: Show specific case types
- **Filter by Status**: Show specific statuses
- **Filter by Urgency**: Show by urgency level
- **Sort Options**: Sort by date, priority, amount, etc.

### Processing Cases

#### Manual Triage
1. **Select a Case**: Click on a case in the queue
2. **Review Information**: Examine case details and documents
3. **Run Triage**: Click "Run Triage" to process with AI agents
4. **Review Results**: Examine triage recommendations
5. **Apply or Override**: Accept AI recommendations or make manual adjustments
6. **Complete Processing**: Mark case as processed

#### Batch Processing
1. **Select Multiple Cases**: Use checkboxes to select cases
2. **Batch Triage**: Run triage on multiple cases simultaneously
3. **Review Results**: Examine results for all cases
4. **Bulk Actions**: Apply actions to multiple cases

### Quality Assurance

#### Review Process
- **Random Sampling**: Review random cases for quality
- **High-Risk Cases**: Special attention to high-risk cases
- **Override Analysis**: Review cases where AI was overridden
- **Performance Monitoring**: Track accuracy and processing times

#### Feedback Loop
- **Rate Results**: Provide feedback on triage accuracy
- **Report Issues**: Flag problematic cases or system issues
- **Suggest Improvements**: Contribute to system enhancement

## Analytics and Reporting

### Dashboard Analytics

#### Key Performance Indicators
- **Case Volume**: Number of cases processed over time
- **Processing Time**: Average time to complete triage
- **Accuracy**: Percentage of accurate classifications
- **SLA Compliance**: Adherence to service level agreements

#### Trend Analysis
- **Daily Trends**: Case volume and processing patterns
- **Weekly Patterns**: Weekly processing cycles
- **Monthly Reports**: Monthly performance summaries
- **Seasonal Analysis**: Seasonal variations in case types

### Detailed Reports

#### Case Volume Reports
- **By Case Type**: Volume breakdown by case category
- **By Urgency**: Distribution of urgency levels
- **By Team**: Cases handled by each team
- **By Time Period**: Volume trends over time

#### Performance Reports
- **Processing Time**: Average and distribution of processing times
- **Accuracy Metrics**: Classification and routing accuracy
- **SLA Performance**: SLA adherence and violations
- **Team Performance**: Individual and team performance metrics

#### Risk Analysis
- **Risk Distribution**: Distribution of risk scores
- **High-Risk Cases**: Analysis of high-risk case patterns
- **Fraud Detection**: Potential fraud indicators
- **Compliance Issues**: Compliance violations and trends

### Exporting Data

#### Report Formats
- **CSV Export**: Download data for external analysis
- **PDF Reports**: Generate formatted reports
- **Excel Files**: Export for spreadsheet analysis
- **API Access**: Programmatic access to data

#### Scheduled Reports
- **Daily Reports**: Automatic daily summaries
- **Weekly Reports**: Weekly performance summaries
- **Monthly Reports**: Monthly comprehensive reports
- **Custom Schedules**: Configure custom report schedules

## User Management

### Profile Management

#### Update Profile
1. Click on your username in the top-right corner
2. Select "Profile"
3. Update your information:
   - **Personal Details**: Name, email, phone
   - **Preferences**: Language, timezone, notifications
   - **Security**: Password, two-factor authentication
4. Click "Save Changes"

#### Notification Settings
- **Email Notifications**: Configure email alerts
- **In-App Notifications**: Set up in-app notifications
- **SLA Alerts**: Get notified of SLA violations
- **System Updates**: Receive system update notifications

### Team Management (Admin Only)

#### User Administration
- **Add Users**: Create new user accounts
- **Edit Users**: Modify user information and permissions
- **Deactivate Users**: Temporarily disable accounts
- **Delete Users**: Permanently remove accounts

#### Role Management
- **Agent**: Basic case processing capabilities
- **Manager**: Team management and reporting access
- **Admin**: Full system administration
- **Custom Roles**: Create custom permission sets

#### Team Configuration
- **Create Teams**: Set up new processing teams
- **Assign Users**: Add users to teams
- **Set Capacities**: Define team processing capacity
- **Configure Routing**: Set up automatic case routing

## System Settings

### General Settings

#### System Configuration
- **Case Types**: Configure available case types
- **Urgency Levels**: Define urgency level options
- **SLA Targets**: Set service level agreement targets
- **Risk Thresholds**: Configure risk assessment parameters

#### Integration Settings
- **External Systems**: Configure external system connections
- **API Keys**: Manage API access keys
- **Webhooks**: Set up webhook notifications
- **Data Sources**: Configure data import sources

### Security Settings

#### Authentication
- **Password Policy**: Configure password requirements
- **Session Timeout**: Set session duration limits
- **Two-Factor Auth**: Enable 2FA for enhanced security
- **Login Attempts**: Configure failed login handling

#### Data Protection
- **PII Detection**: Configure sensitive data detection
- **Data Retention**: Set data retention policies
- **Audit Logging**: Configure audit trail settings
- **Encryption**: Manage data encryption settings

## Troubleshooting

### Common Issues

#### Login Problems
- **Forgot Password**: Use password reset functionality
- **Account Locked**: Contact administrator for unlock
- **Invalid Credentials**: Verify username and password
- **Session Expired**: Log in again

#### Case Processing Issues
- **Triage Failures**: Check case data completeness
- **Slow Processing**: Verify system resources
- **Incorrect Results**: Review and provide feedback
- **System Errors**: Contact technical support

#### Performance Issues
- **Slow Loading**: Check internet connection
- **Timeout Errors**: Verify system availability
- **Data Not Loading**: Refresh page or clear cache
- **Export Failures**: Check file size limits

### Getting Help

#### Support Resources
- **Help Documentation**: Access built-in help system
- **Video Tutorials**: Watch instructional videos
- **FAQ Section**: Common questions and answers
- **Contact Support**: Reach out to technical support

#### Feedback and Suggestions
- **Feature Requests**: Suggest new features
- **Bug Reports**: Report system issues
- **Improvement Ideas**: Share enhancement suggestions
- **User Experience**: Provide UX feedback

## Best Practices

### Case Creation
- **Clear Titles**: Use descriptive, specific titles
- **Complete Descriptions**: Provide comprehensive case details
- **Accurate Classification**: Select appropriate case types
- **Proper Urgency**: Assess urgency accurately

### Case Processing
- **Regular Review**: Monitor queue regularly
- **Quality Focus**: Prioritize accuracy over speed
- **Documentation**: Maintain clear case notes
- **Escalation**: Escalate complex cases promptly

### Data Management
- **Regular Backups**: Ensure data is backed up
- **Data Validation**: Verify data accuracy
- **Privacy Compliance**: Follow data protection guidelines
- **Audit Trail**: Maintain complete audit records

### System Usage
- **Regular Updates**: Keep system updated
- **Security Awareness**: Follow security best practices
- **Performance Monitoring**: Monitor system performance
- **Training**: Stay updated on new features