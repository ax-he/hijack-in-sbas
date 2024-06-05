# hijack-in-sbas
This project is solely for conducting prefix hijack experiments in SBAS. The original repository can be found at [scion-sbas](https://github.com/netsys-lab/seed-emulator/tree/feature/scion-sbas/).

The document of bgp prefix hijacking in seed-emulator can be found at [B04-bgp-prefix-hijacking](https://github.com/seed-labs/seed-emulator/tree/master/examples/B04-bgp-prefix-hijacking).

To run this experiment, you need to install the seed-emulator and the SCION framework.

There are two methods to perform BGP prefix hijack operations.

## Using automated scripts
1. Replace the original ['edunet_pure_bgp.py'](https://github.com/netsys-lab/seed-emulator/blob/feature/scion-sbas/examples/scion/S12-edunet/edunet_pure_bgp.py) with this 'edunet_pure_bgp.py' file.

2. Place the 'hijack.sh' file in the same directory as 'edunet_pure_bgp.py', which might be "examples/scion/S12-edunet/".

3. Create a "utility/" directory under the "scion/" directory, and place the 'experiment.py' file in that directory.

4. Run the 'edunet_pure_bgp.py': `python3 edunet_pure_bgp.py`.

5. Check the visualization container with `http://127.0.0.1:8080/map.html` (`cd client/` and `docker-compose build && docker-compose up`).

6. Once the hijack starts, check the success of the attack by examining the routing information table of other ASes or by sending ping results to the victim.
For example, the default attacker is AS11, and the victim is AS101. We can evaluate the attack results by observing the status of AS13:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On the 13/cs1 node, run `ping 10.101.0.71` to check the return results of the ping command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On the 13/br0 node, run `birdc show route all` to check the latest routing table of AS13.

7. You can change the attacker and the victim by modifying the hijackAS function (line 343 in edunet_pure_bgp.py)
