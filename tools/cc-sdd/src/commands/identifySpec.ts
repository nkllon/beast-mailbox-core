#!/usr/bin/env node

import { promises as fs } from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';

type IdentifyOptions = {
  specPath: string;
  owner?: string;
  featureName?: string;
  generateNewId?: boolean;
  idOverride?: string;
  dryRun?: boolean;
  verbose?: boolean;
};

type SpecJson = Record<string, unknown> & {
  feature_name: string;
  id?: string;
  owner?: string;
  hash?: { algorithm: string; value: string };
  created_at?: string;
  updated_at?: string;
};

const normalizeNewlines = (input: string): string => input.replace(/\r\n?/g, '\n');

const fileExists = async (target: string): Promise<boolean> => {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
};

const findSpecPath = async (input: string): Promise<string> => {
  const resolved = path.resolve(process.cwd(), input);
  const stats = await fs.stat(resolved);
  if (!stats.isDirectory()) {
    throw new Error(`Spec path must be a directory: ${input}`);
  }
  const specPath = path.join(resolved, 'spec.json');
  if (!(await fileExists(specPath))) {
    throw new Error(`Expected spec.json inside ${resolved}`);
  }
  return resolved;
};

const locateSpecByFeature = async (feature: string): Promise<string> => {
  const candidates = [
    path.join(process.cwd(), '.kiro', 'specs', feature),
    path.join(process.cwd(), 'specs', feature),
  ];
  for (const candidate of candidates) {
    if (await fileExists(path.join(candidate, 'spec.json'))) {
      return candidate;
    }
  }
  throw new Error(`Unable to locate spec directory for feature "${feature}"`);
};

const parseArgs = (argv: string[]): IdentifyOptions => {
  const options: IdentifyOptions = { specPath: '' };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    switch (arg) {
      case '--spec':
      case '-s': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --spec');
        options.specPath = next;
        break;
      }
      case '--feature':
      case '-f': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --feature');
        options.featureName = next;
        break;
      }
      case '--owner':
      case '-o': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --owner');
        options.owner = next;
        break;
      }
      case '--regenerate-id':
        options.generateNewId = true;
        break;
      case '--id': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --id');
        options.idOverride = next;
        break;
      }
      case '--dry-run':
        options.dryRun = true;
        break;
      case '--verbose':
        options.verbose = true;
        break;
      case '--help':
      case '-h':
        console.log(`Usage: identify-spec [options]

Options:
  --spec, -s <path>       Path to spec directory (containing spec.json)
  --feature, -f <name>    Feature name under .kiro/specs
  --owner, -o <email>     Owner contact for the spec (required if not set)
  --id <uuid>             Force identifier value
  --regenerate-id         Generate a new identifier even if one exists
  --dry-run               Do not write changes, just report
  --verbose               Print detailed progress
  --help, -h              Show this help message
`);
        process.exit(0);
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return options;
};

const readSpecJson = async (specDir: string): Promise<SpecJson> => {
  const specPath = path.join(specDir, 'spec.json');
  const content = await fs.readFile(specPath, 'utf8');
  const data = JSON.parse(content) as SpecJson;
  if (!data.feature_name) {
    throw new Error(`spec.json missing feature_name at ${specPath}`);
  }
  return data;
};

const computeSpecHash = async (specDir: string): Promise<string> => {
  const hash = createHash('sha256');
  const candidates = ['requirements.md', 'design.md', 'tasks.md'];
  let appended = false;

  for (const filename of candidates) {
    const filePath = path.join(specDir, filename);
    if (await fileExists(filePath)) {
      const content = await fs.readFile(filePath, 'utf8');
      hash.update(filename);
      hash.update('\n');
      hash.update(normalizeNewlines(content));
      hash.update('\n');
      appended = true;
    }
  }

  if (!appended) {
    hash.update(path.basename(specDir));
  }

  return hash.digest('hex');
};

const writeSpecJson = async (specDir: string, data: SpecJson, dryRun: boolean, verbose: boolean): Promise<void> => {
  const specPath = path.join(specDir, 'spec.json');
  const serialized = `${JSON.stringify(data, null, 2)}\n`;
  if (dryRun) {
    if (verbose) {
      console.log(`[dry-run] skipping write to ${specPath}`);
    }
    return;
  }
  await fs.writeFile(specPath, serialized, 'utf8');
};

const identifySpec = async (): Promise<void> => {
  try {
    const args = parseArgs(process.argv.slice(2));

    let resolvedSpecPath: string | undefined;
    if (args.specPath) {
      resolvedSpecPath = await findSpecPath(args.specPath);
    } else if (args.featureName) {
      resolvedSpecPath = await locateSpecByFeature(args.featureName);
    } else {
      throw new Error('Provide either --spec <path> or --feature <name>.');
    }

    const specJson = await readSpecJson(resolvedSpecPath);

    const owner = args.owner ?? specJson.owner ?? process.env.KIRO_DEFAULT_OWNER;
    if (!owner) {
      throw new Error('Owner is required. Pass --owner or set KIRO_DEFAULT_OWNER.');
    }

    let identifier = specJson.id;
    if (args.idOverride) {
      identifier = args.idOverride;
    } else if (!identifier || args.generateNewId) {
      identifier = randomUUID();
    }

    const hashValue = await computeSpecHash(resolvedSpecPath);
    const updatedAt = new Date().toISOString();

    const updatedSpec: SpecJson = {
      ...specJson,
      id: identifier,
      owner,
      hash: { algorithm: 'sha256', value: hashValue },
      updated_at: updatedAt,
    };

    await writeSpecJson(resolvedSpecPath, updatedSpec, args.dryRun ?? false, args.verbose ?? false);

    console.log(
      `Spec "${updatedSpec.feature_name}" identified:\n` +
        `  directory: ${resolvedSpecPath}\n` +
        `  id:        ${updatedSpec.id}\n` +
        `  owner:     ${updatedSpec.owner}\n` +
        `  hash:      ${updatedSpec.hash?.value}\n` +
        `  updated:   ${updatedSpec.updated_at}${args.dryRun ? ' (dry-run)' : ''}`,
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`identify-spec error: ${message}`);
    process.exit(1);
  }
};

void identifySpec();
#!/usr/bin/env node

import { promises as fs } from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';

type IdentifyOptions = {
  specPath: string;
  owner?: string;
  generateNewId?: boolean;
  idOverride?: string;
  dryRun?: boolean;
  verbose?: boolean;
};

type SpecJson = Record<string, unknown> & {
  feature_name: string;
  id?: string;
  owner?: string;
  hash?: { algorithm: string; value: string };
  created_at?: string;
  updated_at?: string;
};

const normalizeNewlines = (input: string): string => input.replace(/\r\n?/g, '\n');

const fileExists = async (target: string): Promise<boolean> => {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
};

const findSpecPath = async (input: string): Promise<string> => {
  const resolved = path.resolve(process.cwd(), input);
  const stat = await fs.stat(resolved);
  if (stat.isDirectory()) {
    return resolved;
  }
  throw new Error(`Spec path must reference a directory containing spec.json: ${input}`);
};

const locateSpecByFeature = async (feature: string): Promise<string> => {
  const candidates = [
    path.join(process.cwd(), '.kiro', 'specs', feature),
    path.join(process.cwd(), 'specs', feature),
  ];
  for (const candidate of candidates) {
    if (await fileExists(path.join(candidate, 'spec.json'))) {
      return candidate;
    }
  }
  throw new Error(`Unable to locate spec directory for feature "${feature}".`);
};

const parseArgs = (argv: string[]): IdentifyOptions & { featureName?: string } => {
  const opts: IdentifyOptions & { featureName?: string } = {
    specPath: '',
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    switch (arg) {
      case '--spec':
      case '-s': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --spec');
        opts.specPath = next;
        break;
      }
      case '--feature':
      case '-f': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --feature');
        opts.featureName = next;
        break;
      }
      case '--owner':
      case '-o': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --owner');
        opts.owner = next;
        break;
      }
      case '--regenerate-id':
        opts.generateNewId = true;
        break;
      case '--id': {
        const next = argv[++i];
        if (!next) throw new Error('Missing value for --id');
        opts.idOverride = next;
        break;
      }
      case '--dry-run':
        opts.dryRun = true;
        break;
      case '--verbose':
        opts.verbose = true;
        break;
      case '--help':
      case '-h':
        console.log(`Usage: identify-spec [options]

Options:
  --spec, -s <path>       Path to spec directory (containing spec.json)
  --feature, -f <name>    Feature name under .kiro/specs
  --owner, -o <email>     Owner contact for the spec (required if not set)
  --id <uuid>             Force identifier value
  --regenerate-id         Generate a new identifier even if one exists
  --dry-run               Do not write changes, just report
  --verbose               Print detailed progress
  --help, -h              Show this help message
`);
        process.exit(0);
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return opts;
};

const readSpecJson = async (specDir: string): Promise<SpecJson> => {
  const specPath = path.join(specDir, 'spec.json');
  const content = await fs.readFile(specPath, 'utf8');
  const data = JSON.parse(content) as SpecJson;
  if (!data.feature_name) {
    throw new Error(`spec.json missing feature_name at ${specPath}`);
  }
  return data;
};

const computeSpecHash = async (specDir: string): Promise<string> => {
  const hash = createHash('sha256');
  const candidates = ['requirements.md', 'design.md', 'tasks.md'];
  let appended = false;

  for (const filename of candidates) {
    const filePath = path.join(specDir, filename);
    if (await fileExists(filePath)) {
      const content = await fs.readFile(filePath, 'utf8');
      hash.update(filename);
      hash.update('\n');
      hash.update(normalizeNewlines(content));
      hash.update('\n');
      appended = true;
    }
  }

  if (!appended) {
    // fall back to identifier content to keep hash deterministic
    hash.update(path.basename(specDir));
  }

  return hash.digest('hex');
};

const writeSpecJson = async (specDir: string, data: SpecJson, dryRun: boolean, verbose: boolean): Promise<void> => {
  const specPath = path.join(specDir, 'spec.json');
  const serialized = `${JSON.stringify(data, null, 2)}\n`;
  if (dryRun) {
    if (verbose) {
      console.log(`--dry-run set, skipping write to ${specPath}`);
    }
    return;
  }
  await fs.writeFile(specPath, serialized, 'utf8');
};

const identifySpec = async (): Promise<void> => {
  try {
    const argv = process.argv.slice(2);
    const options = parseArgs(argv);

    let resolvedSpecPath: string;
    if (options.specPath) {
      resolvedSpecPath = await findSpecPath(options.specPath);
    } else if (options.featureName) {
      resolvedSpecPath = await locateSpecByFeature(options.featureName);
    } else {
      throw new Error('Specify either --spec <path> or --feature <name>.');
    }

    const specJson = await readSpecJson(resolvedSpecPath);

    const ownerFromEnv = process.env.KIRO_DEFAULT_OWNER;
    const owner = options.owner ?? specJson.owner ?? ownerFromEnv;
    if (!owner) {
      throw new Error('Owner is required. Provide --owner or set KIRO_DEFAULT_OWNER.');
    }

    let identifier = specJson.id;
    if (options.idOverride) {
      identifier = options.idOverride;
    } else if (!identifier || options.generateNewId) {
      identifier = randomUUID();
    }

    const hashValue = await computeSpecHash(resolvedSpecPath);
    const now = new Date().toISOString();

    const updatedSpec: SpecJson = {
      ...specJson,
      id: identifier,
      owner,
      hash: {
        algorithm: 'sha256',
        value: hashValue,
      },
      updated_at: now,
    };

    await writeSpecJson(resolvedSpecPath, updatedSpec, options.dryRun ?? false, options.verbose ?? false);

    console.log(
      `Spec "${updatedSpec.feature_name}" identified:\n` +
        `  directory: ${resolvedSpecPath}\n` +
        `  id:        ${updatedSpec.id}\n` +
        `  owner:     ${updatedSpec.owner}\n` +
        `  hash:      ${updatedSpec.hash?.value}\n` +
        `  updated:   ${updatedSpec.updated_at}${options.dryRun ? ' (dry-run)' : ''}`,
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`identify-spec error: ${message}`);
    process.exit(1);
  }
};

void identifySpec();

