using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Gateway.Extensions;

public static class GatewayConfiguration
{
    public static IServiceCollection AddHermesGateway(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddReverseProxy()
                .LoadFromConfig(configuration.GetSection("ReverseProxy"));
        
        return services;
    }
}
