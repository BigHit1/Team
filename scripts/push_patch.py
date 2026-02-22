"""
热更新推送脚本
将修改的文件复制到项目热更目录
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Optional


class HotUpdatePusher:
    """热更新推送器"""
    
    def __init__(self, project_path: str):
        """
        初始化推送器
        
        Args:
            project_path: UE5 项目路径
        """
        self.project_path = Path(project_path)
        self.paks_dir = self.project_path / "Content" / "Paks" / "HotUpdate"
        self.files_dir = self.paks_dir / "Files"
    
    def push(
        self,
        patch_dir: str,
        file_types: Optional[List[str]] = None
    ) -> bool:
        """
        推送热更新文件
        
        Args:
            patch_dir: 包含修改文件的目录
            file_types: 要处理的文件类型
        
        Returns:
            bool: 是否成功
        """
        patch_path = Path(patch_dir)
        
        if not patch_path.exists():
            print(f"❌ 补丁目录不存在: {patch_path}")
            return False
        
        print(f"📦 推送热更新到: {self.paks_dir}")
        
        # 确保目录存在
        self.files_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集文件
        files = self._collect_files(patch_path, file_types)
        
        if not files:
            print("⚠️ 没有找到要推送的文件")
            return False
        
        print(f"📄 找到 {len(files)} 个文件")
        
        # 复制文件
        pushed_count = 0
        for src_path, rel_path in files:
            dest_path = self.files_dir / rel_path
            
            # 确保目标目录存在
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            try:
                shutil.copy2(src_path, dest_path)
                print(f"  ✅ {rel_path}")
                pushed_count += 1
            except Exception as e:
                print(f"  ❌ {rel_path}: {e}")
        
        print(f"\n🎉 成功推送 {pushed_count}/{len(files)} 个文件")
        print(f"\n💡 下次游戏启动时会自动挂载热更新")
        
        return pushed_count > 0
    
    def _collect_files(
        self,
        patch_dir: Path,
        file_types: Optional[List[str]] = None
    ) -> List[tuple]:
        """
        收集要推送的文件
        
        Returns:
            [(源文件路径, 相对路径), ...]
        """
        if file_types is None:
            file_types = ['lua', 'json', 'txt', 'csv', 'ini', 'cfg', 'uasset', 'umap']
        
        files = []
        
        for root, dirs, filenames in os.walk(patch_dir):
            for filename in filenames:
                file_path = Path(root) / filename
                
                # 检查文件类型
                if file_path.suffix.lower().lstrip('.') not in file_types:
                    continue
                
                # 跳过隐藏和临时文件
                if filename.startswith('.') or filename.endswith(('.tmp', '.bak')):
                    continue
                
                # 计算相对路径（去掉顶层目录名）
                try:
                    rel_path = file_path.relative_to(patch_dir)
                    files.append((file_path, rel_path))
                except ValueError:
                    continue
        
        return files
    
    def list_updates(self) -> List[str]:
        """列出当前热更新目录中的文件"""
        if not self.files_dir.exists():
            return []
        
        files = []
        for file_path in self.files_dir.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.files_dir)
                files.append(str(rel_path))
        
        return sorted(files)
    
    def clear_updates(self) -> bool:
        """清空热更新文件"""
        if not self.files_dir.exists():
            return True
        
        try:
            shutil.rmtree(self.files_dir)
            self.files_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 已清空热更新文件")
            return True
        except Exception as e:
            print(f"❌ 清空失败: {e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='热更新推送脚本')
    parser.add_argument('--project', required=True, help='UE5 项目路径')
    parser.add_argument('--patch-dir', required=True, help='包含修改文件的目录')
    parser.add_argument('--type', help='文件类型（逗号分隔），例如：lua,json,uasset')
    parser.add_argument('--list', action='store_true', help='列出当前热更新文件')
    parser.add_argument('--clear', action='store_true', help='清空热更新文件')
    
    args = parser.parse_args()
    
    pusher = HotUpdatePusher(args.project)
    
    # 列出当前文件
    if args.list:
        files = pusher.list_updates()
        if files:
            print("📁 当前热更新文件:")
            for f in files:
                print(f"   - {f}")
        else:
            print("📁 热更新目录为空")
        sys.exit(0)
    
    # 清空文件
    if args.clear:
        success = pusher.clear_updates()
        sys.exit(0 if success else 1)
    
    # 推送文件
    file_types = None
    if args.type:
        file_types = [t.strip() for t in args.type.split(',')]
    
    success = pusher.push(args.patch_dir, file_types)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
