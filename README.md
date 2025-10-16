# Function that validates Basic Authentication for Oracle API Gateway

This function validates Basic Authentication credentials for multiple users against configuration stored in Oracle Functions. It is designed to work as an authentication provider for Oracle API Gateway.

## Prerequisites

Before you deploy this sample function, make sure you have run steps A, B
and C of the [Oracle Functions Quick Start Guide for Cloud Shell](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartcloudshell.htm)

- A - Set up your tenancy
- B - Create application
- C - Set up your Cloud Shell dev environment

## List Applications

Assuming you have successfully completed the prerequisites, you should see your
application in the list of applications.

```
fn ls apps
```

## Review and Deploy this Function

### Python

This function is written in Python and validates Basic Authentication credentials against a JSON configuration of users.

#### Features

- ✅ **Multiple User Support**: Validate multiple users via JSON configuration
- ✅ **Basic Authentication**: Standard HTTP Basic Auth with Base64 encoding
- ✅ **Fast Validation**: O(1) dictionary lookup for user validation
- ✅ **Comprehensive Logging**: Detailed debug and error logging
- ✅ **API Gateway Compatible**: Works as authentication provider

#### Code

This folder contains the files to deploy the `basicauth-python` function:

- the code of the function, [func.py](./func.py)
- its dependencies, [requirements.txt](./requirements.txt)
- the function metadata, [func.yaml](./func.yaml)

#### Configure Users

![user input icon](./images/userinput.png)

Before deploying, configure the users who will be validated by this function. Use JSON format to define multiple users:

```
fn config app <app-name> VALID_USERS '[{"username":"user1","password":"pass1"},{"username":"user2","password":"pass2"},{"username":"admin","password":"admin123"}]'
```

e.g.

```
fn config app myapp VALID_USERS '[{"username":"user1","password":"pass1"},{"username":"user2","password":"pass2"},{"username":"admin","password":"admin123"}]'
```

**Configuration Limits:**

- Total configuration size: 4KB limit for all Oracle Functions configuration
- User capacity: ~50+ users within 4KB limit

#### Deploy

Deploy the `basicauth-python` function using:

```
fn -v deploy --app <app-name>
```

e.g.

```
fn -v deploy --app myapp
```

#### Test

The command to invoke a function is:

```
fn invoke <app-name> <func-name>
```

To test with valid credentials (user1:pass1), run:

```
echo -n '{"type":"TOKEN","token":"Basic dXNlcjE6cGFzczE="}' | fn invoke myapp basicauth-python
```

The function returns:

```json
{
  "active": true,
  "principal": "user1"
}
```

To test with invalid credentials, run:

```
echo -n '{"type":"TOKEN","token":"Basic dXNlcjE6d3JvbmdwYXNz"}' | fn invoke myapp basicauth-python
```

The function returns:

```json
{
  "active": false,
  "principal": null
}
```

Congratulations! You've just deployed and tested a Basic Authentication function for Oracle API Gateway!

## Request and Response Format

### Request Format

The function expects a JSON payload with the following structure:

```json
{
  "type": "TOKEN",
  "token": "Basic <base64-encoded-username:password>"
}
```

The token should be a Base64-encoded string in the format `username:password`.

**Example:** To encode `user1:pass1`:

```bash
echo -n 'user1:pass1' | base64
# Output: dXNlcjE6cGFzczE=
```

### Response Format

**Success Response** (valid credentials):

```json
{
  "active": true,
  "principal": "user1"
}
```

**Failure Response** (invalid credentials):

```json
{
  "active": false,
  "principal": null
}
```

## Integration with Oracle API Gateway

This function is designed to work as an authentication provider for Oracle API Gateway:

1. **Deploy Function**: Follow the deployment steps above
2. **Configure API Gateway**: Set this function as the authentication provider in your API Gateway deployment
3. **Test Integration**: Make API calls through the gateway with Basic Auth headers
4. **Monitor**: Check both API Gateway and function logs

For more details, see [Oracle API Gateway Documentation](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Concepts/apigatewayoverview.htm).

View function logs using:

```bash
fn logs <app-name> basicauth-python
```

e.g.

```bash
fn logs myapp basicauth-python
```

## Troubleshooting

### Common Issues

**1. "Function initialization error, VALID_USERS configuration not set"**

- Configure VALID_USERS using `fn config app <app-name> VALID_USERS '[...]'`
- Ensure JSON format is valid

**2. "Request error, missing or invalid Basic auth token"**

- Verify token starts with "Basic "
- Check base64 encoding: `echo -n 'username:password' | base64`

**3. Authentication always fails**

- Verify configuration: `fn config app <app-name>`
- Check function logs: `fn logs <app-name> basicauth-python`
- Ensure credentials match configuration exactly

### Debug Steps

1. Check function logs:

   ```bash
   fn logs <app-name> basicauth-python
   ```

2. Verify configuration:

   ```bash
   fn config app <app-name>
   ```

3. Test with known credentials:
   ```bash
   echo -n '{"type":"TOKEN","token":"Basic dXNlcjE6cGFzczE="}' | fn invoke <app-name> basicauth-python
   ```

## Security Considerations

- **Password Storage**:
  - ⚠️ **Important**: Storing passwords directly in function configuration is not ideal for production environments
  - **Recommended**: Use [OCI Vault](https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm) to securely store and retrieve credentials
  - OCI Vault provides centralized secrets management with encryption, access control, and audit capabilities
  - The current implementation uses function configuration for simplicity in development/testing
- **Strong Passwords**: Use strong passwords for production environments
- **Credential Rotation**: Consider rotating credentials regularly
- **HTTPS**: Always use HTTPS for API calls
- **Access Control**: Limit access to function configuration
- **Monitoring**: Monitor authentication logs for suspicious activity

## Additional Resources

For more information:

- [Oracle Functions Documentation](https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm)
- [Oracle API Gateway Documentation](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Concepts/apigatewayoverview.htm)
- [Basic Authentication RFC](https://tools.ietf.org/html/rfc7617)
