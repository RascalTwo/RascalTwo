import subprocess
import json
import os

CLI_INDEX_SNK = """
import * as fs from "fs";
import * as path from "path";
import * as core from "@actions/core";
import { generateContributionSnake } from "./generateContributionSnake";
import { parseOutputsOption } from "./outputsOptions";

(async () => {
	const userName = process.argv[2]
	const outputFilepaths = (process.argv[3] || '').split(',').filter(Boolean)
	if (!userName || !outputFilepaths.length) {
		console.error('Username and Outputs needed')
		process.exit(1)
	}
  try {
    const outputs = parseOutputsOption(outputFilepaths);

    const results = await generateContributionSnake(userName, outputs);

    outputs.forEach((out, i) => {
      const result = results[i];
      if (out?.filename && result) {
        console.log(`💾 writing to ${out?.filename}`);
        fs.mkdirSync(path.dirname(out?.filename), { recursive: true });
        fs.writeFileSync(out?.filename, result);
      }
    });
  } catch (e: any) {
    core.setFailed(`CLI failed with "${e.message}"`);
  }
})();
"""

def update_snake():
	if not os.path.exists('snk'):
		subprocess.call('git clone https://github.com/Platane/snk', shell=True)
	else:
		subprocess.call('cd snk && git checkout .', shell=True)
		subprocess.call('cd snk && git clean -f', shell=True)
		subprocess.call('cd snk && git pull', shell=True)
	subprocess.call('cd snk && npm i', shell=True)
	with open('snk/packages/action/cliIndex.ts', 'w') as f:
		f.write(CLI_INDEX_SNK)
	subprocess.call('cd snk/packages/action && npx ncc build --external canvas --external gifsicle --out dist ./cliIndex.ts', shell=True)
	subprocess.call('cd snk/packages/action && node dist/index.js RascalTwo "../../../assets/github-snake-light.svg?palette=github-light,../../../assets/github-snake-dark.svg?palette=github-dark"', shell=True)
	subprocess.call('git add assets/github-snake*', shell=True)
	hash = subprocess.check_output('git --no-pager log -n1 --oneline --pretty=format:"%H" assets/github-snake-dark.svg', shell=True).decode('utf-8')
	subprocess.call('git amend-to ' + hash, shell=True)

THREED_SETTINGS = {
  "type": "rainbow",
  "backgroundColor": "#eeeeff",
  "foregroundColor": "#0d1117",
  "strongColor": "#47c1ee",
  "weakColor": "#aaaaaa",
  "radarColor": "#47c1ee",
  "growingAnimation": True,
  "saturation": "100%",
  "contribLightness": [
    "50%",
    "50%",
    "50%",
    "50%",
    "50%"
  ],
  "duration": "10s",
  "hueRatio": -10
}


def update_3d():
	if not os.path.exists('github-profile-3d-contrib'):
		subprocess.call('git clone https://github.com/yoshi389111/github-profile-3d-contrib.git', shell=True)
	else:
		subprocess.call('cd github-profile-3d-contrib && git checkout .', shell=True)
		subprocess.call('cd github-profile-3d-contrib && git clean -f', shell=True)
		subprocess.call('cd github-profile-3d-contrib && git pull', shell=True)
	subprocess.call('cd github-profile-3d-contrib && npm i', shell=True)
	for bg, fg, name in [('#eeeeff', '#0d1117', 'light'), ('#0d1117', '#eeeeff', 'dark')]:
		THREED_SETTINGS['backgroundColor'] = bg
		THREED_SETTINGS['foregroundColor'] = fg
		with open('github-profile-3d-contrib/sample-settings/customize.json', 'w') as f:
			json.dump(THREED_SETTINGS, f)
		subprocess.call('cd github-profile-3d-contrib && SETTING_JSON=./sample-settings/customize.json npm run dev RascalTwo', shell=True)
		os.rename('github-profile-3d-contrib/profile-3d-contrib/profile-customize.svg', 'assets/3d-contrib-' + name + '.svg')
	subprocess.call('git add assets/3d-contrib*', shell=True)
	hash = subprocess.check_output('git --no-pager log -n1 --oneline --pretty=format:"%H" assets/3d-contrib-dark.svg', shell=True).decode('utf-8')
	subprocess.call('git amend-to ' + hash, shell=True)

if __name__ == '__main__':
	update_snake()
	update_3d()