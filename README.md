# Hijack-in-SBAS
This project is solely for conducting prefix hijacking experiments in SBAS. The original repository can be found at [scion-sbas](https://github.com/netsys-lab/seed-emulator/tree/feature/scion-sbas/).

The document of performing bgp prefix hijacking in seed-emulator can be found at [B04-bgp-prefix-hijacking](https://github.com/seed-labs/seed-emulator/tree/master/examples/B04-bgp-prefix-hijacking).

To run this experiment, you need to install the seed-emulator and the SCION framework.

## BGP prefix hijack
There are **two** methods to perform BGP prefix hijack operations.

### Using automated scripts
1. Replace the original ['edunet_pure_bgp.py'](https://github.com/netsys-lab/seed-emulator/blob/feature/scion-sbas/examples/scion/S12-edunet/edunet_pure_bgp.py) with this `automated.py` file.

2. Place the 'hijack.sh' file in the same directory as 'automated.py', which might be `examples/scion/S12-edunet/`.

3. Create a `utility/` directory under the `scion/` directory, and place the `experiment.py` file in that directory.

4. Run the 'automated.py': `python3 automated.py`.

5. Check the visualization container with `http://127.0.0.1:8080/map.html` (`cd client/` and `docker-compose build && docker-compose up`). Use `ICMP` filter to better track the status of packet transmission.

6. Once the hijack starts, test the attack by examining the routing information table of other ASes or by sending ping to the victim.
For example, the default attacker is AS11, and the victim is AS101. You can evaluate the attack results by observing the status of AS12:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On the 12/cs1 node, run `ping 10.101.0.71` to check the return results of the ping command.
![image](https://github.com/ax-he/hijack-in-sbas/assets/35193352/9cacc44a-2e79-48d3-a65a-e026af89566d)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On the 12/br0 node, run `birdc show route all` to check the latest routing table of AS12.
![image](https://github.com/ax-he/hijack-in-sbas/assets/35193352/967e7f32-f84f-4a75-8ac0-d3946ed7815d)
Note that the original routing table should be:
![image](https://github.com/ax-he/hijack-in-sbas/assets/35193352/1ce381eb-3077-4030-96f4-a88205cab6d2)

A special phenomenon in this attack is that AS 105 can still successfully access AS 101 through SBAS when its routing policy does not point to AS 101.
![image](https://github.com/ax-he/hijack-in-sbas/assets/35193352/f5be04bd-7607-41f0-aa76-58bfeeeabc6f)
![image](https://github.com/ax-he/hijack-in-sbas/assets/35193352/a79f8de0-b044-4808-93d7-38e10568af5a)
In contrast, the original routing table of AS 105 is as following:
![image](https://github.com/ax-he/hijack-in-sbas/assets/35193352/c37a5ebf-b285-47ed-bffd-4f0587312d84)

7. You can change the attacker and the victim by modifying the hijackAS function (line 343 in edunet_pure_bgp.py)

### Using manual methods
1. Replace the original ['edunet_pure_bgp.py'](https://github.com/netsys-lab/seed-emulator/blob/feature/scion-sbas/examples/scion/S12-edunet/edunet_pure_bgp.py) with this `manual.py` file. Run with `python3 manual.py`

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
