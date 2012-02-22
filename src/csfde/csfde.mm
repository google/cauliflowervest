// Copyright (c) 2011 Google Inc. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Author: Mark Mentovai

#include <pwd.h>
#include <unistd.h>
#include <CoreFoundation/CoreFoundation.h>
#include <DiskArbitration/DiskArbitration.h>
#import <Foundation/Foundation.h>
#include <libgen.h>
#include <objc/runtime.h>
#import <OpenDirectory/OpenDirectory.h>

#include "base/logging.h"
#include "base/mac/scoped_cftyperef.h"
#include "base/mac/scoped_nsautorelease_pool.h"
#include "base/memory/scoped_nsobject.h"
#include "chrome/browser/mac/scoped_ioobject.h"

// Big Enough length to accept recovery passwords from libcsfde
int kRecoveryPasswordLen = 80;

extern "C" {

// libcsfde.dylib

// Creates a new recipe with a single request for CSFDEAddVolumeEncryption,
// and the block algorithm in that request set to |block_algorithm|. The only
// known algorithm is "AES-XTS".
CFMutableArrayRef CSFDECreateNewRecipe(CFStringRef block_algorithm);

// Adds a request to |recipe| to establish a recovery user for password-based
// recovery using a new randomly-generated password, which will be placed in
// |recovery_password|. Returns TRUE on success and FALSE on failure. Use this
// instead of CSFDERequestRecoveryUser to prevent the possibility of a
// keychain-based recovery request being created even in the presence of an
// FDE recovery keychain.
Boolean CSFDERequestIndividualRecoveryUser(
    CFMutableArrayRef recipe,
    char recovery_password[kRecoveryPasswordLen]);

// Adds a request to |recipe| to establish a recovery user. If an FDE recovery
// keychain is present, CSFDERequestAsymmetricRecoveryUser will add a request
// for keychain-based recovery corresponding to the data in that keychain.
// Otherwise, CSFDERequestIndividualRecoveryUser will add a request for
// password-based recovery using a new randomly-generated password. Returns
// the result of CSFDERequestAsymmetricRecoveryUser or
// CSFDERequestIndividualRecoveryUser, which is TRUE on success and FALSE on
// failure.
// |recovery_password| will be set to the recovery password for a request
// prepared by CSFDERequestIndividualRecoveryUser. For a request prepared by
// CSFDERequestAsymmetricRecoveryUser, it will be an empty string.
// |password_recovery_user|, if non-NULL, will be set to FALSE for a request
// prepared by CSFDERequestAsymmetricRecoveryUser and TRUE for a request
// prepared by CSFDERequestIndividualRecoveryUser.
// |req_ref|, if non-NULL, will be set to the request added to |recipe|.
Boolean CSFDERequestRecoveryUser(CFMutableArrayRef recipe,
                                 char recovery_password[kRecoveryPasswordLen],
                                 Boolean* password_recovery_user,
                                 CFDictionaryRef* request);

// Stores a passphrase with the FDE driver in the kernel, returning a handle
// that can be used to refer to the passphrase later.
//
// There appears to be finite storage in the kernel for these, because calling
// this enough times results in it starting to fail at some point, and the
// only cure is a reboot. Maybe when done with the passphrase handles, they
// should be disposed of with CSFDERemovePassphrase. But be careful: make sure
// that CSFDERemovePassphrase doesn't actually remove passphrases from disk.
// More investigation is warranted.
CFStringRef CSFDEStorePassphrase(const char* password);

// Adds a request to |recipe| to allow a user to boot the system from the
// encrypted disk by logging in with a user name and password.
// |user_uuid| is the GeneratedUID Directory Service value.
// |password_handle| is a handle returned by CSFDEStorePassphrase.
// |password_hint| is the AuthenticationHint Directory Service value.
// |user_names| is an array of two CFDataRef objects, the first being the
// user's full name, and the second being the user's account name.
// |full_name| is the RealName Directory Service value.
// |user_icon| is the JPEGPhoto Directory Service value.
// |efi_login_graphics| is an archive returned by EFILoginCopyUserGraphics.
Boolean CSFDERequestOSUserEntry(CFMutableArrayRef recipe,
                                CFStringRef user_uuid,
                                CFStringRef password_handle,
                                CFStringRef password_hint,
                                CFArrayRef user_names,
                                CFStringRef full_name,
                                CFDataRef user_icon,
                                CFDataRef efi_login_graphics);

// EFILogin.framework

// Returns a new archive in a private (but easily understood) format
// containing images for use during EFI login.
// |function| chooses the sort of archive to produce. Known values are 1
// to create user account login graphics, and 4 to create a graphic containing
// Recovery Serial Number and Recovery Record Number data.
// |full_name| is the RealName Directory Service value when |function| is 1,
// and may be NULL when |function| is 4.
// |picture| is the JPEGPhoto Directory Service value when |function| is 1,
// and may be NULL when |function| is 4.
// |password_hint| is the AuthenticationHint Directory Service value when
// |function| is 1, or a recovery password hint when |function| is 4.
// |dictionary| can be NULL if |function| is 1. If |function| is 4, the
// dictionary contains two CFStringRef keys,
// kEFILoginRecoveryServiceSerialNumberKey ("Recovery Serial Number") and
// kEFILoginRecoveryServiceRecordNumberKey ("Recovery Record Number"), each
// with CFStringRef values.
CFDataRef EFILoginCopyUserGraphics(int function,
                                   CFStringRef full_name,
                                   CFDataRef picture,
                                   CFStringRef password_hint,
                                   CFDictionaryRef dictionary);

}  // extern "C"

// DiskManagement.framework

@interface DMManager : NSObject

- (void)setDelegate:(id)delegate;

@end

@interface DMCoreStorage : NSObject

-(DMCoreStorage*)initWithManager:(DMManager*)manager;

-(int)convertDisk:(DADiskRef)disk options:(NSDictionary*)options;

@end

namespace {

// Other tools which run csfde will expect this exit status returned when
// the username/password authentication fails
const int kExitStatusAuthFailed = 99;

const char* g_me;

void LogNSError(const char* function, NSError* error) {
  LOG(ERROR) << function << " failed: " << [[error description] UTF8String];
}

id GetSingleValueForODRecordAttribute(ODRecord* record,
                                      ODAttributeType attribute,
                                      Class expected_class) {
  NSError* error = nil;
  NSArray* array = [record valuesForAttribute:attribute
                                        error:&error];
  if (!array) {
    LOG(WARNING) << "-[ODRecord valuesForAttribute:error:] failed for "
                 << [attribute UTF8String] << ": "
                 << [[error description] UTF8String];
    return nil;
  }

  NSUInteger array_count = [array count];
  if (array_count != 1) {
    LOG(WARNING) << "-[ODRecord valuesForAttribute:error:] returned "
                 << array_count << " results for " << [attribute UTF8String];
    return nil;
  }

  id value = [array objectAtIndex:0];

  if (![value isKindOfClass:expected_class]) {
    LOG(WARNING) << "-[ODRecord valuesForAttribute:error:] returned an "
                 << "object of class " << class_getName([value class])
                 << ", expected " << class_getName(expected_class);
    return nil;
  }

  return value;
}

}  // namespace

@interface DMAsyncDelegate : NSObject {
  BOOL error_;
  NSMutableDictionary *results_;
}

- (void)dmAsyncStartedForDisk:(DADiskRef)disk;
- (void)dmAsyncProgressForDisk:(DADiskRef)disk
                    barberPole:(BOOL)barberPole
                       percent:(float)percent;
- (void)dmAsyncMessageForDisk:(DADiskRef)disk
                       string:(NSString*)string
                   dictionary:(NSDictionary*)dictionary;
- (void)dmAsyncFinishedForDisk:(DADiskRef)disk
                     mainError:(NSError*)mainError  // NSError? Check!
                   detailError:(NSError*)detailError  // NSError? Check!
                    dictionary:(NSDictionary*)dictionary;

- (BOOL)error;
- (NSMutableDictionary*)results;

@end

@implementation DMAsyncDelegate

- (void)dmAsyncStartedForDisk:(DADiskRef)disk {
  fprintf(stderr, "-dmAsyncStartedForDisk:\n");
}

- (void)dmAsyncProgressForDisk:(DADiskRef)disk
                    barberPole:(BOOL)barberPole
                       percent:(float)percent {
  fprintf(stderr, "-dmAsyncProgressForDisk: barberPole:%d percent:%f\n",
          barberPole, percent);
}

- (void)dmAsyncMessageForDisk:(DADiskRef)disk
                       string:(NSString*)string
                   dictionary:(NSDictionary*)dictionary {
  fprintf(stderr, "-dmAsyncMessageForDisk string:%s dictionary:%s\n",
          [string UTF8String], [[dictionary description] UTF8String]);
}

- (void)dmAsyncFinishedForDisk:(DADiskRef)disk
                     mainError:(NSError*)mainError
                   detailError:(NSError*)detailError
                    dictionary:(NSDictionary*)dictionary {
  fprintf(stderr, "-dmAsyncFinishedForDisk: mainError:%s detailError:%s "
                  "dictionary:%s\n",
          [[mainError description] UTF8String],
          [[detailError description] UTF8String],
          [[dictionary description] UTF8String]);

  error_ = mainError || detailError;

  results_ = [dictionary mutableCopy];
  [results_ setValue:[NSNumber numberWithBool:error_] forKey:@"error"];

  CFRunLoopRef run_loop = CFRunLoopGetCurrent();
  CFRunLoopStop(run_loop);
  CFRunLoopWakeUp(run_loop);
}

- (BOOL)error {
  return error_;
}

- (NSMutableDictionary*)results {
  return results_;
}

@end

BOOL IsValidRecoveryPassword(char password[kRecoveryPasswordLen]) {
  /* Expected format is XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
     where X is 0-9A-Z */
  int i;

  for (i=0; i<30; i++) {
    if (i == 29) {
      if (password[i] != '\0')
        return NO;
    }
    else if ((i + 1) % 5 == 0) {
      if (password[i] != '-')
        return NO;
    } else {
      if (!((password[i] >= 'A') && (password[i] <= 'Z')) &&
         (!(password[i] >= '0') && (password[i] <= '9')))
        return NO;
    }
  }
  return YES;
}

int main(int argc, char* argv[]) {
  base::mac::ScopedNSAutoreleasePool autorelease_pool;

  g_me = basename(argv[0]);

  if (argc != 4) {
    fprintf(stderr, "usage: %s <disk_bsd_name> <username> <password>\n", g_me);
    return 1;
  }

  // disk_bsd_name_c should be the root HFS+ filesystem, like "disk0s2".
  const char* disk_bsd_name_c = argv[1];
  const char* username_c = argv[2];

  char* password_tmp_c = NULL;
  char password_tmp_buf[100];

  if (strcmp(argv[3], "-") == 0) {
    fprintf(
        stderr, "Enter password on stdin (note password will be visible): ");
    fgets(password_tmp_buf, arraysize(password_tmp_buf) - 1, stdin);
    if (password_tmp_buf[strlen(password_tmp_buf) - 1] == '\n')
      password_tmp_buf[strlen(password_tmp_buf) - 1] = '\0';
    password_tmp_c = password_tmp_buf;
  } else {
    password_tmp_c = argv[3];
  }

  const char* password_c = password_tmp_c;

  base::mac::ScopedCFTypeRef<DASessionRef> da_session(
      DASessionCreate(NULL));
  if (!da_session) {
    LOG(ERROR) << "DASessionCreate failed";
    return 1;
  }

  // Some scoper should unschedule this.
  DASessionScheduleWithRunLoop(da_session,
                             CFRunLoopGetCurrent(),
                             kCFRunLoopDefaultMode);

  base::mac::ScopedCFTypeRef<DADiskRef> disk_da(
      DADiskCreateFromBSDName(NULL, da_session, disk_bsd_name_c));
  if (!disk_da) {
    LOG(ERROR) << "DADiskCreateFromBSDName failed";
    return 1;
  }

  // Attempt to access the IOMedia object. It's not needed for anything, but
  // if disk_bsd_name_c doesn't refer to a real disk, it will fail, allowing
  // early validation of the disk.
  ScopedIOObject<io_service_t> disk_iomedia(DADiskCopyIOMedia(disk_da));
  if (!disk_iomedia) {
    LOG(ERROR) << "DADiskCopyIOMedia failed";
    fprintf(stderr, "%s: error opening disk %s\n", g_me, disk_bsd_name_c);
    return 1;
  }

  // Since the IOMedia object is no longer needed, release it.
  disk_iomedia.reset();

  NSError* error = nil;
  ODSession* od_session = [ODSession sessionWithOptions:nil error:&error];
  if (!od_session) {
    LogNSError("+[ODSession sessionWithOptions:error:", error);
    return 1;
  }

  ODNode* authentication_node =
      [ODNode nodeWithSession:od_session
                         type:kODNodeTypeAuthentication
                        error:&error];
  if (!authentication_node) {
    LogNSError("+[ODNode nodeWithSession:type:error:]", error);
    return 1;
  }

  NSString* username = [NSString stringWithUTF8String:username_c];
  ODQuery* query = [ODQuery queryWithNode:authentication_node
                           forRecordTypes:kODRecordTypeUsers
                                attribute:kODAttributeTypeRecordName
                                matchType:kODMatchEqualTo
                              queryValues:username
                         returnAttributes:kODAttributeTypeStandardOnly
                           maximumResults:1
                                    error:&error];
  if (!query) {
    LogNSError("+[ODQuery queryWithNode:...]", error);
    return 1;
  }

  NSArray* results = [query resultsAllowingPartial:NO error:&error];
  if (!results) {
    LogNSError("-[ODQuery resultsAllowingPartial:error:]", error);
    return 1;
  }

  NSUInteger result_count = [results count];
  if (result_count != 1) {
    LOG(ERROR) << "+[ODQuery queryWithNode:...] returned " << result_count
               << " results";
    fprintf(stderr, "%s: user %s not found\n", g_me, username_c);
    return 1;
  }

  ODRecord* record = [results objectAtIndex:0];

  NSString* password = [NSString stringWithUTF8String:password_c];
  BOOL authenticated = [record verifyPassword:password error:&error];
  if (!authenticated) {
    LogNSError("-[ODRecord verifyPassword:error:]", error);
    fprintf(stderr, "%s: authentication failed for user %s\n",
            g_me, username_c);
    return kExitStatusAuthFailed;
  }

  // user_uuid is required.
  NSString* user_uuid = GetSingleValueForODRecordAttribute(record,
                                                           kODAttributeTypeGUID,
                                                           [NSString class]);
  if (!user_uuid) {
    LOG(ERROR) << "Missing required attribute "
               << [kODAttributeTypeGUID UTF8String];
    return 1;
  }

  // These elements are not required.
  NSString* full_name =
      GetSingleValueForODRecordAttribute(record,
                                         kODAttributeTypeFullName,
                                         [NSString class]);
  NSString* password_hint =
      GetSingleValueForODRecordAttribute(record,
                                         kODAttributeTypeAuthenticationHint,
                                         [NSString class]);
  NSData* user_icon =
      GetSingleValueForODRecordAttribute(record,
                                         kODAttributeTypeJPEGPhoto,
                                         [NSData class]);

  base::mac::ScopedCFTypeRef<CFDataRef> efi_login_graphics(
      EFILoginCopyUserGraphics(1,
                               (CFStringRef)full_name,
                               (CFDataRef)user_icon,
                               (CFStringRef)password_hint,
                               NULL));

  base::mac::ScopedCFTypeRef<CFMutableArrayRef> recipe(
      CSFDECreateNewRecipe(CFSTR("AES-XTS")));

  char recovery_password[kRecoveryPasswordLen];
  Boolean password_recovery_user;
  Boolean rv_boolean = CSFDERequestRecoveryUser(recipe,
                                                recovery_password,
                                                &password_recovery_user,
                                                NULL);
  if (!rv_boolean) {
    LOG(ERROR) << "CSFDERequestRecoveryUser failed";
    return 1;
  }

  if (password_recovery_user) {
    if (IsValidRecoveryPassword(recovery_password)) {
      LOG(INFO) << "Using a password-based recovery user with "
                << "recovery password";
    } else {
      LOG(ERROR) << "Unexpected format of recovery password: "
                 << recovery_password;
      return 1;
    }
  } else {
    LOG(INFO) << "Using a keychain-based recovery user";
  }

  CFStringRef password_handle = CSFDEStorePassphrase(password_c);
  if (!password_handle) {
    LOG(ERROR) << "CSFDEStorePassphrase failed";
    return 1;
  }

  NSData* username_data = [username dataUsingEncoding:NSUTF8StringEncoding];
  NSData* full_name_data = [full_name dataUsingEncoding:NSUTF8StringEncoding];
  NSArray* user_names = [NSArray arrayWithObjects:full_name_data,
                                                  username_data,
                                                  nil];

  rv_boolean = CSFDERequestOSUserEntry(recipe,
                                      (CFStringRef)user_uuid,
                                      password_handle,
                                      (CFStringRef)password_hint,
                                      (CFArrayRef)user_names,
                                      (CFStringRef)full_name,
                                      (CFDataRef)user_icon,
                                      efi_login_graphics);
  if (!rv_boolean) {
    LOG(ERROR) << "CSFDERequestOSUserEntry failed";
    return 1;
  }

  scoped_nsobject<DMManager> dm_manager([[DMManager alloc] init]);
  if (!dm_manager) {
    LOG(ERROR) << "+[DMManager alloc] or -[DMManager init] failed";
    return 1;
  }

  scoped_nsobject<DMAsyncDelegate> dm_async_delegate(
      [[DMAsyncDelegate alloc] init]);
  [dm_manager setDelegate:dm_async_delegate];

  scoped_nsobject<DMCoreStorage> dm_core_storage(
      [[DMCoreStorage alloc] initWithManager:dm_manager]);
  if (!dm_core_storage) {
    LOG(ERROR) << "+[DMCoreStorage alloc] or "
               << "-[DMCoreStorage initWithManager:] failed";
    return 1;
  }

  NSDictionary* options =
      [NSDictionary dictionaryWithObjectsAndKeys:(NSDictionary*)recipe.get(),
                                                 @"FDERecipe",
                                                 nil];

  int rv_int = [dm_core_storage convertDisk:disk_da options:options];
  if (rv_int != 0) {
    LOG(ERROR) << "-[DMCoreStorage convertDisk:options:] failed: "
               << rv_int;
    return 1;
  }

  // Use an NSRunLoop?
  CFRunLoopRun();

  if ([dm_async_delegate error]) {
    LOG(ERROR) << "-[DMCoreStorage convertDisk:options:] failed (see above)";
    return 1;
  }

  NSMutableDictionary* csfde_results = [dm_async_delegate results];
  if (password_recovery_user) {
    [csfde_results setValue:[NSString stringWithUTF8String:recovery_password]
                     forKey:@"recovery_password"];
  }

  NSString *error_description;
  NSData* csfde_plist = [NSPropertyListSerialization
      dataFromPropertyList:csfde_results
                    format:NSPropertyListXMLFormat_v1_0
          errorDescription:&error_description];

  if (error_description) {
    LOG(ERROR) << "-NSPropertyListSerialization "
               << "dataFromPropertyList:format:errorDescription "
               << [error_description UTF8String];
    return 1;
  }

  const char* bytes = static_cast<const char *>([csfde_plist bytes]);
  NSUInteger length = [csfde_plist length];

  if (bytes && length > 0) {
    while (length > 0) {
      int offset = 0;

      ssize_t result = write(fileno(stdout), bytes + offset, length);
      if (result <= 0) {
        PLOG(ERROR) << "write(stdout, plist...)";
        return 1;
      }
      offset += result;
      length -= result;
    }
  } else {
    LOG(ERROR) << "-[NSData bytes] == NULL or -[NSData length] == 0";
  }

  return 0;
}
