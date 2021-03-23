# xcodeproj

`xcodeproj` is a utility for interacting with Xcode's xcodeproj bundle format.

It expects some level of understanding of the internals of the pbxproj format and schemes. Note that this tool only reads projects. It does not write out any changes. If you are looking for more advanced functionality like this, I recommend looking at the Ruby gem of the same name (which is unaffiliated in anyway). 

To learn more about the format, you can look at any of these locations:

* <http://www.monobjc.net/xcode-project-file-format.html>
* <https://www.rubydoc.info/gems/xcodeproj/Xcodeproj/Project>

## Getting Started

Loading a project is very simple:

```python
project = xcodeproj.XcodeProject("/path/to/project.xcodeproj")
```

From here you can explore the project in different ways:

```python

# Get all targets
for target in project.targets:
    print(target.name)

# Print from the root level, 2 levels deep (.project is a property on the root 
# project as other properties such as .schemes are also available)
for item1 in project.project.main_group.children:
    print(item1)
    if not isinstance(item1, xcodeproj.PBXGroup):
        continue

    for item2 in item1.children:
        print("\t", item2)

# Check that all files referenced in the project exist on disk
for item in project.fetch_type(xcodeproj.PBXFileReference).values():
    assert os.path.exists(item.absolute_path())

# You can access the raw objects map directly:
obj = project.objects["key here"]

# For any object you have, you can access its key/identifier via the 
# `.object_key` property
key = obj.object_key
```

Note: This library is "lazy". Many things aren't calculated until they are used. This time will be inconsequential on smaller projects, but on larger ones, it can save quite a bit of time due to not parsing the entire project on load. These properties are usually stored though so that subsequent accesses are instant.

## Note on Scheme Support
There's no DTD for xcscheme files, so the implementation has been guessed. There will definitely be holes that still need to be patched in it though. Please open an issue if you find any, along with a sample xcscheme file.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
