# Get the local username
data "external" "get_username" {
  program = ["../setup/get_username.sh"]
}