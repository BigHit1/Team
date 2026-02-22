"""
热更新 Pak 打包脚本
将修改的文件打包成热更 Pak，并复制到项目目录
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class HotUpdatePacker:
    """热更新打包器"""
    
    def __init__(self, project_path: str):
        """
        初始化打包器
        
        Args:
            project_path: UE5 项目路径
        """
        self.project_path = Path(project_path)
        self.paks_dir = self.project_path / "Content" / "Paks" / "HotUpdate"
        self.ue5_pak_exe = self._find_unrealpak()
    
    def _find_unrealpak(self) -> Optional[Path]:
        """查找 UnrealPak.exe"""
        # 常见的 UnrealPak 路径
        possible_paths = [
            self.project_path / "Plugins" / "Sandbox" / "Saved" / "Tools" / "UnrealPak.exe",
            self.project_path / ".." / ".." / "Engine" / "Binaries" / "Win64" / "UnrealPak.exe",
            "C:\\Program Files\\Epic Games\\UE_5.3\\Engine\\Binaries\\Win64\\UnrealPak.exe",
            "C:\\Program Files\\Epic Games\\UE_5.4\\Engine\\Binaries\\Win64\\UnrealPak.exe",
            "D:\\UE5\\UE_5.3\\Engine\\Binaries\\Win64\\UnrealPak.exe",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                print(f"✅ 找到 UnrealPak: {path}")
                return Path(path)
        
        print("⚠️ 未找到 UnrealPak.exe，需要手动指定")
        return None
    
    def pack(
        self,
        source_dir: str,
        output_name: Optional[str] = None,
        patch_version: int = 1
    ) -> bool:
        """
        打包热更新
        
        Args:
            source_dir: 源文件目录（包含要热更的文件）
            output_name: 输出 Pak 名称（不带扩展名）
            patch_version: 补丁版本号
        
        Returns:
            bool: 是否成功
        """
        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f"❌ 源目录不存在: {source_path}")
            return False
        
        # 生成输出文件名
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"HotUpdate_v{patch_version}_{timestamp}"
        
        output_pak = self.paks_dir / f"{output_name}_P.pak"
        
        # 确保目录存在
        self.paks_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 开始打包热更新")
        print(f"   源目录: {source_path}")
        print(f"   输出: {output_pak}")
        
        # 收集文件
        files = self._collect_files(source_path)
        
        if not files:
            print("⚠️ 没有找到要打包的文件")
            return False
        
        print(f"📄 找到 {len(files)} 个文件")
        
        # 如果有 UnrealPak，直接打包
        if self.ue5_pak_exe:
            success = self._pack_with_unrealpak(files, output_pak)
        else:
            # 否则创建文件列表，手动打包
            success = self._create_pak_manifest(files, output_pak)
        
        if success:
            print(f"✅ 热更新打包成功: {output_pak}")
            print(f"\n💡 下次游戏启动时会自动挂载此 Pak")
        
        return success
    
    def _collect_files(self, source_dir: Path) -> List[Dict]:
        """收集要打包的文件"""
        files = []
        
        # 支持的文件类型
        allowed_extensions = {
            '.lua', '.json', '.txt', '.csv', '.ini', '.cfg',
            '.uasset', '.uexp', '.ubulk',  # UE5 资源
            '.umap', '.uworld', '.uinst',
            '.dll', '.so', '.dylib',  # 动态库
        }
        
        for root, dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = Path(root) / filename
                
                # 跳过隐藏文件和临时文件
                if filename.startswith('.') or filename.endswith(('.tmp', '.bak', '.orig')):
                    continue
                
                # 检查文件类型
                if file_path.suffix.lower() not in allowed_extensions:
                    continue
                
                # 计算相对于源目录的路径
                rel_path = file_path.relative_to(source_dir)
                
                files.append({
                    'path': str(file_path),
                    'relative_path': str(rel_path),
                    'size': file_path.stat().st_size
                })
        
        return files
    
    def _pack_with_unrealpak(self, files: List[Dict], output_pak: Path) -> bool:
        """使用 UnrealPak 打包"""
        try:
            # 创建临时响应文件
            response_file = output_pak.with_suffix('.txt')
            
            with open(response_file, 'w', encoding='utf-8') as f:
                for file_info in files:
                    # UnrealPak 格式: "相对路径" "绝对路径"
                    f.write(f'"{file_info["relative_path"]}" "{file_info["path"]}"\n')
            
            # 构建命令
            cmd = [
                str(self.ue5_pak_exe),
                str(output_pak),
                f"@{response_file}",
                "-CreateEmpty"
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            # 执行打包
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 清理响应文件
            response_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print(f"✅ UnrealPak 打包成功")
                return True
            else:
                print(f"❌ UnrealPak 打包失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 打包过程出错: {e}")
            return False
    
    def _create_pak_manifest(self, files: List[Dict], output_pak: Path) -> bool:
        """创建 Pak 清单文件（备选方案）"""
        try:
            # 创建清单
            manifest = {
                'pak_name': output_pak.name,
                'created_at': datetime.now().isoformat(),
                'file_count': len(files),
                'files': files
            }
            
            manifest_file = output_pak.with_suffix('.json')
            
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            print(f"📝 已创建清单文件: {manifest_file}")
            print(f"💡 提示: 需要使用 UnrealPak.exe 进行实际打包")
            
            # 复制文件到热更目录
            print(f"\n📂 复制文件到热更目录...")
            for file_info in files:
                src = Path(file_info['path'])
                rel_path = Path(file_info['relative_path'])
                dest = self.paks_dir / "Files" / rel_path
                
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                print(f"   ✅ {rel_path}")
            
            print(f"\n⚠️ 注意: 文件已复制，但需要手动打包成 .pak")
            print(f"   运行: UnrealPak.exe {output_pak} -CreateEmpty")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建清单失败: {e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='热更新 Pak 打包脚本')
    parser.add_argument('--project', required=True, help='UE5 项目路径')
    parser.add_argument('--source', required=True, help='源文件目录（包含要热更的文件）')
    parser.add_argument('--output', help='输出 Pak 名称（可选）')
    parser.add_argument('--version', type=int, default=1, help='补丁版本号')
    
    args = parser.parse_args()
    
    # 打包
    packer = HotUpdatePacker(args.project)
    success = packer.pack(args.source, args.output, args.version)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
