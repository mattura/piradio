while ! ping -c1 www.google.com &>/dev/null; do sleep 1; done #Wait for DHCP
ip=`ip addr show scope global | grep inet | cut -d' ' -f6 | cut -d/ -f1`
echo -e '\e[36;1m'
echo -e '       ,                       _     _ _                        '
echo -e '      /#\\        __ _ _ __ ___| |__ | (_)_ __  _   ___  __      '
echo -e '     /###\\      / _` | `__/ __|  _ \\| | | `_ \\| | | \\ \\/ /      '
echo -e '    /#####\\    | (_| | | | (__| | | | | | | | | |_| |>  <       '
echo -e '   /##,_,##\\    \\__,_|_|  \\___|_| |_|_|_|_| |_|\\__,_/_/\\_\\      '
echo -e '  /##(   )##\\\e[1;37m     On the \e[31;1mRaspberry Pi\e[1;37m - Back to basics.\e[36;1m        '
echo -e ' /#.--   --.#\\                                                  '
echo -e "/\`           \`\\         \e[30;1mIP Address: \e[33;0m $ip                               "
echo -e '\e[0m'
