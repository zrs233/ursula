#!/bin/bash
function usage () {
  cat << EOF

Usage: $0 [OPTION] user_name(sn)
Removes password policy for a particular user.
The parameter passed is the 'name' attribute as described in keystone user-list command
Example: $0 -r monitoring

If name contains a space then wrap it with quotes
Example: $0 -s "FirstName LastName"

Options::
-r remove policy
-s show policy
-l list locked users
-u unlock a user
-a add policy to a user
-c change a user's password


EOF
}

if [ ! $1 ]; then
  usage
  exit 1
fi

declare -A options
for num
do

   if [[ $num == -* ]]; then
      getopts ":rsulac" opt
	  case "$opt" in
        r)
          options['r']=1
          check_user_name=1
          ;;
        a)
          options['a']=1
          check_user_name=1
          ;;
        u)
          options['u']=1
          check_user_name=1
          ;;
        l)
          options['l']=1
          ;;
        c)
          options['c']=1
          check_user_name=1
          ;;
        \?)
          echo "Invalid option: -$OPTARG" >&2
          usage
          exit 1
          ;;
        :)
          echo "Option -$OPTARG requires an argument." >&2
          usage
          exit 1
          ;;
      esac
   elif [ ! ${options['user']} ]; then
      options['user']=$num
   else
      echo "Invalid option '$num', remove it!!"
      usage
      exit 1
   fi
done




user_name=${options['user']}

if [ $check_user_name ]; then

  if [ ! "$user_name" ]; then
    echo "User name is not specified"
    usage
    exit 400
  fi

  dn=`ldapsearch -LLL -x -D {{openldap.openldap_user_dn}} -b {{openldap.organizationalUnit}} -w {{openldap.root_password}} -s sub sn="$user_name" -o ldif-wrap=no | head -1`

  if [ ! $dn ]; then
    echo "\"$user_name\" not found"
    exit 404
  fi

  echo "dn is $dn"

fi
if [ ${options['r']} ]; then
   echo "Attempting to remove password policy from user $user_name"
   dir_location=/tmp/pwd_policy_remove
   mkdir -p $dir_location

   file_name=`uuidgen`

   echo "$dn" > $dir_location/$file_name.ldif
   echo "changeType: modify" >> $dir_location/$file_name.ldif
   echo "add: pwdPolicySubentry" >> $dir_location/$file_name.ldif
   echo "pwdPolicySubentry: {{openldap.password_nopolicy_dn}}" >> $dir_location/$file_name.ldif
   ldapmodify  -D {{openldap.root_dn}} -w {{openldap.root_password}} -f $dir_location/$file_name.ldif
fi


if [ ${options['l']} ]; then
   ldapsearch -D  {{openldap.root_dn}} -w {{openldap.root_password}} -b {{openldap.organizationalUnit}} -s sub pwdAccountLockedTime=* | grep sn
fi


if [ ${options['u']} ]; then
   echo "Attempting to unlock  user $user_name"
   dir_location=/tmp/user_unlock
   mkdir -p $dir_location

   file_name=`uuidgen`

   echo "$dn" > $dir_location/$file_name.ldif
   echo "changeType: modify" >> $dir_location/$file_name.ldif
   echo "delete: pwdAccountLockedTime" >> $dir_location/$file_name.ldif
   ldapmodify  -D {{openldap.root_dn}} -w {{openldap.root_password}} -f $dir_location/$file_name.ldif
fi
if [ ${options['a']} ]; then
   echo "Attempting to add password policy for user $user_name"
   dir_location=/tmp/pwd_policy_add
   mkdir -p $dir_location

   file_name=`uuidgen`

   echo "$dn" > $dir_location/$file_name.ldif
   echo "changeType: modify" >> $dir_location/$file_name.ldif
   echo "delete: pwdPolicySubentry" >> $dir_location/$file_name.ldif
   ldapmodify  -D {{openldap.root_dn}} -w {{openldap.root_password}} -f $dir_location/$file_name.ldif
fi

if [ ${options['c']} ]; then
    echo "Attempting to change password for  user $user_name"
    stty -echo
    read -p "Enter the new password: " pass; echo
    read -p "Confirm password: " confirm_pass; echo
    stty echo
    if [ "$pass" != "$confirm_pass" ]; then
        echo "EROR: Passwords do not match"
        exit 4
    fi
    file_name=`uuidgen`
    dir_location=/tmp/change_password
    mkdir -p $dir_location
    echo "$dn " > $dir_location/$file_name.ldif
    echo "changeType: modify" >>$dir_location/$file_name.ldif
    echo "replace: userPassword" >> $dir_location/$file_name.ldif
    echo "userPassword: $pass" >> $dir_location/$file_name.ldif
    ldapmodify -D {{openldap.root_dn}} -w {{openldap.root_password}} -f $dir_location/$file_name.ldif
fi

