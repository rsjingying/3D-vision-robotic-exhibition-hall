from pathlib import Path
import shutil,json
src=Path('robot-assets/source');out=Path('dist/models');lic=out/'licenses';lic.mkdir(exist_ok=True)
for name,path in [('KUKA-repository-Apache-2.0.txt',src/'kuka/LICENSE'),('KUKA-package.xml',src/'kuka/kuka_kr210_support/package.xml'),('ABB-Apache-2.0.txt',src/'abb/abb_irb4600_support/LICENSE'),('ABB-package.xml',src/'abb/abb_irb4600_support/package.xml')]:shutil.copyfile(path,lic/name)
shutil.copyfile(src/'provenance.json',out/'provenance.json')
(out/'README.txt').write_text('''VISION FLOW / Industrial Robot Models

KUKA KR 210 L150
ROS-Industrial kuka_experimental / kuka_kr210_support
Pinned commit: 8d9292b04a22628b1b78d989e2ddd3abb913bf92
https://github.com/ros-industrial/kuka_experimental/tree/8d9292b04a22628b1b78d989e2ddd3abb913bf92/kuka_kr210_support
Original root LICENSE: Apache-2.0. Original package.xml declares BSD.
Both upstream declarations are preserved in licenses/; the root license does
not resolve the upstream package's differing declaration. Retain attribution
and verify the asset-specific terms before redistributing in commercial work.

ABB IRB 4600-40/2.55
ROS-Industrial abb / abb_irb4600_support
Pinned commit: 45f4769d826cf3ac62a65495f2db67b78b0c81df
https://github.com/ros-industrial/abb/tree/45f4769d826cf3ac62a65495f2db67b78b0c81df/abb_irb4600_support
Upstream license: Apache-2.0; retained in licenses/.

Converted from DAE visual meshes and URDF joints into GLB. Original mesh
colors, physical robot scale, joint origins, axes and limits are retained.
provenance.json records original source URLs and SHA-256 digests.
GLB files and metadata were converted by VISION FLOW, not downloaded as OEM
certified models. Community assets do not imply manufacturer endorsement.
The grippers, camera, stands, conveyors, bins and factory are concept models.
Six-axis inverse kinematics drive illustrative trajectories. No collision,
controller dynamics, certified safety or cycle-time validation is provided.

Three.js and loader utilities: MIT license, see ../vendor/LICENSE.txt.
''')
