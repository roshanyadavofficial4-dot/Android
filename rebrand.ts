import * as fs from 'fs';
import * as path from 'path';

function walkSync(dir: string, filelist: string[] = []) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filepath = path.join(dir, file);
    if (fs.statSync(filepath).isDirectory()) {
      if (file !== 'node_modules' && file !== '.git') {
        walkSync(filepath, filelist);
      }
    } else {
      if (filepath.endsWith('.py') || filepath.endsWith('.md') || filepath.endsWith('.sh') || filepath.endsWith('.txt') || filepath.endsWith('.json')) {
        filelist.push(filepath);
      }
    }
  }
  return filelist;
}

const files = walkSync('.');
for (const file of files) {
  let content = fs.readFileSync(file, 'utf8');
  let original = content;
  
  // Specific replacements first
  content = content.replace(/jarvis_logger/g, 'arya_logger');
  content = content.replace(/jarvis_hud/g, 'arya_hud');
  content = content.replace(/JarvisHUD/g, 'AryaHUD');
  content = content.replace(/JarvisOS/g, 'AryaOS');
  
  // General replacements
  content = content.replace(/JARVIS_OS/g, 'ARYA_OS');
  content = content.replace(/JARVIS/g, 'A.R.Y.A.');
  content = content.replace(/Jarvis/g, 'A.R.Y.A.');
  
  // Any remaining lowercase jarvis (like in imports or file paths)
  content = content.replace(/jarvis/g, 'arya');

  if (content !== original) {
    fs.writeFileSync(file, content, 'utf8');
    console.log(`Updated ${file}`);
  }
}

// Rename files if they contain jarvis
for (const file of files) {
  const basename = path.basename(file);
  if (basename.includes('jarvis')) {
    const newname = basename.replace(/jarvis/g, 'arya');
    const newpath = path.join(path.dirname(file), newname);
    fs.renameSync(file, newpath);
    console.log(`Renamed ${file} to ${newpath}`);
  }
}
