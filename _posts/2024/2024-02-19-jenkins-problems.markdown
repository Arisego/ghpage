---
layout: post
title:  Jenkins使用时的问题记录
tags: []
---

有个Jenkins挂在服务器上好久没动过了，年后上去看了下发现居然完全挂掉了。

## 空间不足

还没搞清楚问题前，Jenkins就完全访问不了了，直接在命令行拉起服务，提示

> Jenkins failed to create a temporary file in /tmp: java.io.IOException: No space left on device

搜索了下发现是空间不足了，可以参考[这里](https://docs.cloudbees.com/docs/cloudbees-ci-kb/latest/best-practices/deleting-old-builds-best-strategy-for-cleanup-and-disk-space-management)的操作


由于我这边已经连服务都拉不起来了，只能手动删除一些缓存

```shell
cd /var/lib/jenkins/jobs/my_awsome_job/
rm -r builds/
```

然后就可以拉起Jenkins了，按照上面的文章配置了下自动清除，后续观察下有没有问题。

## 升级失败

出现错误：

```log
Err:6 https://pkg.jenkins.io/debian-stable binary/ Release.gpg
  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 5BA31D57EF5975CA
Fetched 833 B in 1s (616 B/s)
Reading package lists... Done
W: An error occurred during the signature verification. The repository is not updated and the previous index files will be used. GPG error: https://pkg.jenkins.io/debian-stable binary/ Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 5BA31D57EF5975CA
W: Failed to fetch http://pkg.jenkins.io/debian-stable/binary/Release.gpg  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 5BA31D57EF5975CA
```

参考了[这个资料](https://www.jenkins.io/blog/2023/03/27/repository-signing-keys-changing/)，似乎是密钥变更导致的。直接复制黏贴后就能升级了。

```shell
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
```

