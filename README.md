# Hijack-in-SBAS
This project is solely for conducting prefix hijacking experiments in SBAS. The original repository can be found at [scion-sbas](https://github.com/netsys-lab/seed-emulator/tree/feature/scion-sbas/).

The document of performing bgp prefix hijacking in seed-emulator can be found at [B04-bgp-prefix-hijacking](https://github.com/seed-labs/seed-emulator/tree/master/examples/B04-bgp-prefix-hijacking).

To run this experiment, you need to install the seed-emulator and the SCION framework.

## BGP prefix hijack
There are **two** methods to perform BGP prefix hijack operations.

### Using automated scripts
1. Replace the original ['edunet_pure_bgp.py'](https://github.com/netsys-lab/seed-emulator/blob/feature/scion-sbas/examples/scion/S12-edunet/edunet_pure_bgp.py) with this 'edunet_pure_bgp.py' file.

2. Place the 'hijack.sh' file in the same directory as 'edunet_pure_bgp.py', which might be `examples/scion/S12-edunet/`.

3. Create a `utility/` directory under the `scion/` directory, and place the 'experiment.py' file in that directory.

4. Run the 'edunet_pure_bgp.py': `python3 edunet_pure_bgp.py`.

5. Check the visualization container with `http://127.0.0.1:8080/map.html` (`cd client/` and `docker-compose build && docker-compose up`). Use `ICMP` filter to better track the status of packet transmission.

6. Once the hijack starts, test the attack by examining the routing information table of other ASes or by sending ping to the victim.
For example, the default attacker is AS11, and the victim is AS101. You can evaluate the attack results by observing the status of AS13:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On the 13/cs1 node, run `ping 10.101.0.71` to check the return results of the ping command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On the 13/br0 node, run `birdc show route all` to check the latest routing table of AS13.

7. You can change the attacker and the victim by modifying the hijackAS function (line 343 in edunet_pure_bgp.py)

### Using manual methods
1. Run the **original** ['edunet_pure_bgp.py'](https://github.com/netsys-lab/seed-emulator/blob/feature/scion-sbas/examples/scion/S12-edunet/edunet_pure_bgp.py): `python3 edunet_pure_bgp.py`.

2. `cd output/` and run `docker-compose build && docker-compose up`.

3. Check the visualization container with `http://127.0.0.1:8080/map.html` (`cd client/` and `docker-compose build && docker-compose up`).

4. Select an attacker and a victim (we will continue to use AS11 and AS101 as examples). Go to the container, which is 11/br0, go to the `/etc/bird` folder, and open the BGP configuration file 'bird.conf'. Add the following to the end of the configuration file.
```
protocol static hijacks {
    ipv4 {
        table t_bgp;
    };
    route 10.101.0.0/24 via 10.11.0.71   { bgp_large_community.add(LOCAL_COMM); };
    route 10.101.1.0/24 via 10.11.0.71 { bgp_large_community.add(LOCAL_COMM); };
}
```
After making the change, ask the BGP router to reload configuration file using the command: `birdc configure`.

5. Test the attack by examining the routing information table of other ASes (`birdc show route all`) or by sending ping to the victim (`ping 10.101.0.71`).

## SCION connectivity
The SCION commands can only be used on the control router (cs1). Use `scion ping 71-101,10.101.0.71` to check SCION connectivity.
