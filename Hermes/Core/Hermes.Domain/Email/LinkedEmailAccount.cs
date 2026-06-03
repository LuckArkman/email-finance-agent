using System;
using Hermes.Domain.Common;

namespace Hermes.Domain.Email;

/// <summary>
/// Represents an email account linked by a user/tenant so the Hermes Email 
/// Worker can synchronize their inbox and extract invoices automatically.
/// </summary>
public class LinkedEmailAccount : BaseEntity
{
    /// <summary>Provider identifier: 'google', 'outlook', or 'imap'</summary>
    public string Provider { get; set; } = string.Empty;

    /// <summary>The email address of the linked account.</summary>
    public string EmailAddress { get; set; } = string.Empty;

    /// <summary>OAuth2 access token (encrypted at rest in production).</summary>
    public string AccessToken { get; set; } = string.Empty;

    /// <summary>OAuth2 refresh token for silent re-authentication.</summary>
    public string RefreshToken { get; set; } = string.Empty;

    /// <summary>Whether this account is actively being synced.</summary>
    public bool IsActive { get; set; } = true;

    /// <summary>UTC timestamp of the last successful sync run.</summary>
    public DateTime? LastSyncedAt { get; set; }
}
