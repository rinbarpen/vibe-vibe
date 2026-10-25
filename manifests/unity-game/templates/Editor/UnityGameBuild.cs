// OPTIONAL template: review, then copy to Assets/Editor/UnityGameBuild.cs.
// The installer never adds this file to Assets. Uses enabled Build Settings scenes.
// Example: unity_cli.py build --project . --target StandaloneLinux64
//   --execute-method UnityGameBuild.Build --output Builds/linux-001/MyGame
// The helper supplies -buildReport PATH. This records BuildReport + output hashes;
// a successful build does not establish device launch, signing or store acceptance.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class UnityGameBuild
{
    [Serializable]
    public class FileEvidence
    {
        public string path;
        public long bytes;
        public string sha256;
    }

    [Serializable]
    public class BuildEvidence
    {
        public int schema_version = 1;
        public string result;
        public string target;
        public string output;
        public string[] scenes = new string[0];
        public long errors;
        public long warnings;
        public FileEvidence[] files = new FileEvidence[0];
    }

    // Keep in sync with unity_cli.player_bundle_roots. For directory targets the
    // entire output is included; standalone players also own their _Data + libraries.
    static IEnumerable<string> BundleRoots(string output, BuildTarget target)
    {
        var roots = new List<string> { output };
        if (target == BuildTarget.StandaloneWindows || target == BuildTarget.StandaloneWindows64 || target == BuildTarget.StandaloneLinux64)
        {
            var parent = Path.GetDirectoryName(output);
            roots.Add(Path.Combine(parent, Path.GetFileNameWithoutExtension(output) + "_Data"));
            foreach (var name in new[] { "UnityPlayer.dll", "UnityPlayer.so", "GameAssembly.dll", "GameAssembly.so", "UnityCrashHandler32.exe", "UnityCrashHandler64.exe", "MonoBleedingEdge", "baselib.dll", "WinPixEventRuntime.dll", "D3D12" })
                roots.Add(Path.Combine(parent, name));
        }
        return roots;
    }

    static IEnumerable<string> BundleFiles(string output, BuildTarget target)
    {
        foreach (var root in BundleRoots(output, target))
        {
            if (File.Exists(root)) yield return root;
            else if (Directory.Exists(root))
                foreach (var file in Directory.GetFiles(root, "*", SearchOption.AllDirectories))
                    yield return file;
        }
    }

    static FileEvidence HashFile(string file)
    {
        using (var hash = SHA256.Create())
        using (var input = File.OpenRead(file))
            return new FileEvidence { path = Path.GetFullPath(file), bytes = input.Length,
                sha256 = BitConverter.ToString(hash.ComputeHash(input)).Replace("-", "").ToLowerInvariant() };
    }

    static void SaveReport(string path, BuildEvidence evidence)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path));
        var temporary = path + ".tmp-" + Guid.NewGuid().ToString("N");
        try
        {
            File.WriteAllText(temporary, JsonUtility.ToJson(evidence, true) + "\n");
            File.Move(temporary, path); // Do not replace an earlier evidence record.
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }

    public static void Build()
    {
        string reportPath = null;
        var evidence = new BuildEvidence { result = "Failed", errors = 1 };
        try
        {
            var args = Environment.GetCommandLineArgs();
            var index = Array.IndexOf(args, "-buildOutput");
            if (index < 0 || index + 1 >= args.Length || string.IsNullOrWhiteSpace(args[index + 1]))
                throw new ArgumentException("Expected -buildOutput PATH");
            var output = Path.GetFullPath(args[index + 1]);
            evidence.output = output;
            var reportIndex = Array.IndexOf(args, "-buildReport");
            reportPath = reportIndex >= 0 && reportIndex + 1 < args.Length
                ? Path.GetFullPath(args[reportIndex + 1]) : output + ".build-result.json";
            if (File.Exists(reportPath) || Directory.Exists(reportPath))
                throw new IOException("Build report already exists: " + reportPath);
            if (File.Exists(output) || Directory.Exists(output))
                throw new IOException("Build output already exists: " + output);
            var scenes = EditorBuildSettings.scenes.Where(scene => scene.enabled).Select(scene => scene.path).ToArray();
            evidence.scenes = scenes;
            if (scenes.Length == 0)
                throw new InvalidOperationException("Enable at least one scene in Build Settings");
            var target = EditorUserBuildSettings.activeBuildTarget; // selected by -buildTarget
            evidence.target = target.ToString();
            foreach (var companion in BundleRoots(output, target).Skip(1))
                if (File.Exists(companion) || Directory.Exists(companion))
                    throw new IOException("Existing player bundle companion is preserved; select a fresh bundle directory: " + companion);
            var group = BuildPipeline.GetBuildTargetGroup(target);
            if (!BuildPipeline.IsBuildTargetSupported(group, target))
                throw new InvalidOperationException("Platform module is unavailable: " + target);
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = output,
                target = target,
                options = BuildOptions.None
            });
            evidence.result = report.summary.result.ToString();
            evidence.target = report.summary.platform.ToString();
            evidence.output = Path.GetFullPath(report.summary.outputPath);
            evidence.errors = report.summary.totalErrors;
            evidence.warnings = report.summary.totalWarnings;
            evidence.files = BundleFiles(output, target).Distinct().OrderBy(file => file, StringComparer.Ordinal).Select(HashFile).ToArray();
            SaveReport(reportPath, evidence);
            if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                throw new InvalidOperationException("Build failed: " + report.summary.result + ", errors=" + report.summary.totalErrors);
            Debug.Log("UnityGameBuild succeeded: " + output + "; report=" + reportPath);
            EditorApplication.Exit(0);
        }
        catch (Exception error)
        {
            if (reportPath != null && !File.Exists(reportPath) && !Directory.Exists(reportPath))
            {
                try { evidence.result = "Failed"; evidence.errors = Math.Max(1L, evidence.errors); SaveReport(reportPath, evidence); }
                catch (Exception reportError) { Debug.LogException(reportError); }
            }
            Debug.LogException(error);
            EditorApplication.Exit(1);
        }
    }
}
