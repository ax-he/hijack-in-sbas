#!/bin/bash
command="/bin/cat <<EOM >>/etc/bird/bird.conf
protocol static hijacks {
    ipv4 {
        table t_bgp;
    };
    route 10.$1.0.0/24 via 10.$2.0.71   { bgp_large_community.add(LOCAL_COMM); };
    route 10.$1.1.0/24 via 10.$2.0.71 { bgp_large_community.add(LOCAL_COMM); };
}
EOM"

docker exec -it as${2}r-br0-10.${2}.0.254 /bin/zsh -c "$command"
